"""CUMCM 建模手最小基线模板。

目标：先快速得到“可解释、可复现、可验证”的结果，再根据赛题升级模型。
运行示例：
    python CUMCM_Python最小模板.py --demo all --out demo_output

模板使用合成数据演示，不代表任何真实赛题结论。比赛时应替换数据、变量名、
目标函数、约束和验证策略，并在论文中解释这些改动的现实含义。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    silhouette_score,
)
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt


RANDOM_SEED = 2026
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def make_output_dir(path: str | Path) -> Path:
    """创建并返回结果目录；比赛中所有图表和指标都应集中落盘。"""
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_figure(fig: plt.Figure, path: Path) -> None:
    """以论文可用分辨率保存图像。"""
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def to_jsonable(value: Any) -> Any:
    """把 NumPy/Pandas 标量转换成 JSON 可序列化对象。"""
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def audit_dataframe(data: pd.DataFrame, output_dir: Path) -> dict[str, Any]:
    """执行建模前最低限度的数据审计并保存证据表。"""
    missing = data.isna().sum().sort_values(ascending=False)
    duplicate_rows = int(data.duplicated().sum())
    numeric = data.select_dtypes(include=np.number)

    data.describe(include="all").T.to_csv(
        output_dir / "data_summary.csv", encoding="utf-8-sig"
    )
    pd.DataFrame(
        {
            "missing_count": missing,
            "missing_rate": missing / max(len(data), 1),
            "dtype": data.dtypes.astype(str),
        }
    ).to_csv(output_dir / "missing_and_types.csv", encoding="utf-8-sig")

    audit = {
        "rows": len(data),
        "columns": len(data.columns),
        "duplicate_rows": duplicate_rows,
        "total_missing": int(missing.sum()),
        "numeric_columns": list(numeric.columns),
        "constant_columns": [
            column for column in data.columns if data[column].nunique(dropna=False) <= 1
        ],
    }
    return audit


def regression_baseline(
    features: pd.DataFrame,
    target: pd.Series,
    output_dir: Path,
) -> dict[str, float]:
    """岭回归 + K 折样本外预测；适合作为多数回归题的第一基线。"""
    if len(features) < 10:
        raise ValueError("回归交叉验证至少建议 10 个样本。")

    model = Pipeline(
        [("scale", StandardScaler()), ("model", Ridge(alpha=1.0))]
    )
    splitter = KFold(n_splits=min(5, len(features)), shuffle=True, random_state=RANDOM_SEED)
    prediction = cross_val_predict(model, features, target, cv=splitter)

    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(target, prediction))),
        "mae": float(mean_absolute_error(target, prediction)),
        "r2": float(r2_score(target, prediction)),
    }

    fig, ax = plt.subplots(figsize=(6, 5), layout="constrained")
    ax.scatter(target, prediction, alpha=0.72, edgecolor="none")
    low = float(min(target.min(), prediction.min()))
    high = float(max(target.max(), prediction.max()))
    ax.plot([low, high], [low, high], "--", color="#d95f02", label="理想预测")
    ax.set(xlabel="真实值", ylabel="交叉验证预测值", title="岭回归：样本外预测")
    ax.legend()
    save_figure(fig, output_dir / "regression_cv.png")

    pd.DataFrame({"actual": target, "prediction": prediction}).to_csv(
        output_dir / "regression_predictions.csv", index=False, encoding="utf-8-sig"
    )
    return metrics


def classification_baseline(
    features: pd.DataFrame,
    target: pd.Series,
    output_dir: Path,
) -> dict[str, float]:
    """逻辑回归 + 分层交叉验证；报告准确率和宏平均 F1。"""
    class_counts = target.value_counts()
    if len(class_counts) < 2 or class_counts.min() < 2:
        raise ValueError("分类至少需要 2 个类别，且每类至少 2 个样本。")

    splits = int(min(5, class_counts.min()))
    splitter = StratifiedKFold(n_splits=splits, shuffle=True, random_state=RANDOM_SEED)
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )
    prediction = cross_val_predict(model, features, target, cv=splitter)
    metrics = {
        "accuracy": float(accuracy_score(target, prediction)),
        "macro_f1": float(f1_score(target, prediction, average="macro")),
    }

    fig, ax = plt.subplots(figsize=(5.5, 5), layout="constrained")
    ConfusionMatrixDisplay.from_predictions(target, prediction, ax=ax, cmap="Blues")
    ax.set_title("逻辑回归：分层交叉验证混淆矩阵")
    save_figure(fig, output_dir / "classification_confusion_matrix.png")
    return metrics


def clustering_baseline(
    features: pd.DataFrame,
    output_dir: Path,
    max_k: int = 8,
) -> dict[str, Any]:
    """标准化后比较 K-Means 的轮廓系数，并用 PCA 二维展示。"""
    scaled = StandardScaler().fit_transform(features)
    upper_k = min(max_k, len(features) - 1)
    if upper_k < 2:
        raise ValueError("聚类至少需要 3 个样本。")

    scores: dict[int, float] = {}
    labels_by_k: dict[int, np.ndarray] = {}
    for cluster_count in range(2, upper_k + 1):
        model = KMeans(
            n_clusters=cluster_count,
            n_init=20,
            random_state=RANDOM_SEED,
        )
        labels = model.fit_predict(scaled)
        scores[cluster_count] = float(silhouette_score(scaled, labels))
        labels_by_k[cluster_count] = labels

    best_k = max(scores, key=scores.get)
    coordinates = PCA(n_components=2, random_state=RANDOM_SEED).fit_transform(scaled)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    axes[0].plot(list(scores), list(scores.values()), marker="o")
    axes[0].set(xlabel="聚类数 k", ylabel="轮廓系数", title="聚类数选择")
    axes[1].scatter(
        coordinates[:, 0],
        coordinates[:, 1],
        c=labels_by_k[best_k],
        cmap="tab10",
        alpha=0.78,
    )
    axes[1].set(xlabel="PCA 1", ylabel="PCA 2", title=f"K-Means 结果（k={best_k}）")
    save_figure(fig, output_dir / "clustering_selection.png")

    return {"best_k": int(best_k), "silhouette_scores": scores}


def entropy_topsis(
    decision_matrix: np.ndarray,
    benefit_flags: list[bool],
) -> tuple[np.ndarray, np.ndarray]:
    """熵权-TOPSIS 基线。

    benefit_flags=True 表示越大越好；False 表示越小越好。
    使用前必须解释指标口径，并对权重和正向化方法做扰动分析。
    """
    matrix = np.asarray(decision_matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != len(benefit_flags):
        raise ValueError("决策矩阵列数必须与 benefit_flags 长度一致。")
    if not np.isfinite(matrix).all():
        raise ValueError("TOPSIS 输入不能包含缺失值或无穷值。")

    column_min = matrix.min(axis=0)
    column_range = matrix.max(axis=0) - column_min
    normalized = (matrix - column_min) / np.where(column_range == 0, 1.0, column_range)
    for column, is_benefit in enumerate(benefit_flags):
        if not is_benefit:
            normalized[:, column] = 1.0 - normalized[:, column]

    epsilon = 1e-12
    proportions = normalized / np.where(
        normalized.sum(axis=0) == 0,
        1.0,
        normalized.sum(axis=0),
    )
    entropy_scale = 1.0 / np.log(max(len(matrix), 2))
    entropy = -entropy_scale * np.sum(
        proportions * np.log(proportions + epsilon), axis=0
    )
    information = np.where(column_range == 0, 0.0, 1.0 - entropy)
    weights = information / information.sum() if information.sum() > 0 else np.full(
        matrix.shape[1], 1.0 / matrix.shape[1]
    )

    weighted = normalized * weights
    best = weighted.max(axis=0)
    worst = weighted.min(axis=0)
    distance_best = np.linalg.norm(weighted - best, axis=1)
    distance_worst = np.linalg.norm(weighted - worst, axis=1)
    score = distance_worst / (distance_best + distance_worst + epsilon)
    return weights, score


def linear_program_demo() -> dict[str, Any]:
    """演示线性规划：max 3x+2y，满足资源约束。"""
    result = linprog(
        c=[-3.0, -2.0],
        A_ub=[[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]],
        b_ub=[4.0, 2.0, 3.0],
        bounds=[(0, None), (0, None)],
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"线性规划失败：{result.message}")
    decision = result.x
    constraint_slack = np.array([4.0, 2.0, 3.0]) - np.array(
        [[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]]
    ) @ decision
    return {
        "x": decision,
        "maximum_objective": -result.fun,
        "minimum_constraint_slack": float(constraint_slack.min()),
        "solver_message": result.message,
    }


def graph_demo() -> dict[str, Any]:
    """演示带权图最短路；真实题中边权必须说明单位和来源。"""
    graph = nx.Graph()
    graph.add_weighted_edges_from(
        [
            ("A", "B", 4.0),
            ("A", "C", 2.0),
            ("B", "D", 6.0),
            ("C", "D", 3.0),
            ("C", "E", 5.0),
            ("D", "E", 1.0),
        ]
    )
    path = nx.shortest_path(graph, source="A", target="E", weight="weight")
    length = nx.shortest_path_length(graph, source="A", target="E", weight="weight")
    return {"shortest_path": path, "path_length": float(length)}


def time_series_baseline(series: pd.Series, output_dir: Path) -> dict[str, float]:
    """严格按时间留出测试集，对比朴素法与 Holt/ETS；禁止随机切分。"""
    if len(series) < 36:
        raise ValueError("演示模板要求至少 36 个等间隔观测。")
    test_size = max(6, int(round(len(series) * 0.2)))
    train = series.iloc[:-test_size]
    test = series.iloc[-test_size:]
    naive = np.repeat(train.iloc[-1], test_size)

    try:
        model = ExponentialSmoothing(
            train,
            trend="add",
            seasonal="add",
            seasonal_periods=12,
            initialization_method="estimated",
        ).fit(optimized=True)
    except ValueError:
        model = Holt(train, initialization_method="estimated").fit(optimized=True)
    forecast = np.asarray(model.forecast(test_size), dtype=float)

    metrics = {
        "naive_mae": float(mean_absolute_error(test, naive)),
        "ets_mae": float(mean_absolute_error(test, forecast)),
        "ets_rmse": float(np.sqrt(mean_squared_error(test, forecast))),
    }

    fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
    ax.plot(series.index, series.values, label="观测", color="#264653")
    ax.plot(test.index, naive, "--", label="朴素基线", color="#e76f51")
    ax.plot(test.index, forecast, label="Holt/ETS", color="#2a9d8f")
    ax.axvline(test.index[0], color="gray", linestyle=":", label="测试集起点")
    ax.set(xlabel="时间", ylabel="数值", title="时间留出验证")
    ax.legend(ncol=2)
    save_figure(fig, output_dir / "time_series_holdout.png")
    return metrics


def one_at_a_time_sensitivity(
    model: Callable[[dict[str, float]], float],
    base_parameters: dict[str, float],
    relative_change: float = 0.10,
) -> pd.DataFrame:
    """单因素敏感性基线；高维/强交互时再升级 Morris 或 Sobol。"""
    base_output = float(model(base_parameters))
    rows: list[dict[str, float | str]] = []
    for parameter, base_value in base_parameters.items():
        for direction in (-1.0, 1.0):
            changed = dict(base_parameters)
            changed[parameter] = base_value * (1.0 + direction * relative_change)
            output = float(model(changed))
            relative_output_change = (
                (output - base_output) / abs(base_output) if base_output != 0 else np.nan
            )
            rows.append(
                {
                    "parameter": parameter,
                    "parameter_change": direction * relative_change,
                    "output": output,
                    "relative_output_change": relative_output_change,
                }
            )
    return pd.DataFrame(rows)


def synthetic_dataset() -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """生成可重复演示数据；真实赛题严禁用合成值冒充题目结果。"""
    rng = np.random.default_rng(RANDOM_SEED)
    features = pd.DataFrame(
        rng.normal(size=(180, 5)), columns=[f"feature_{index}" for index in range(1, 6)]
    )
    regression_target = (
        2.4 * features["feature_1"]
        - 1.3 * features["feature_2"]
        + 0.8 * features["feature_3"] ** 2
        + rng.normal(scale=0.75, size=len(features))
    ).rename("continuous_target")
    classification_target = (
        regression_target > regression_target.median()
    ).astype(int).rename("class_target")

    periods = 72
    time = np.arange(periods)
    time_series = pd.Series(
        50 + 0.35 * time + 5 * np.sin(2 * np.pi * time / 12) + rng.normal(0, 1.2, periods),
        index=pd.date_range("2020-01-01", periods=periods, freq="MS"),
        name="monthly_value",
    )
    return features, regression_target, classification_target, time_series


def run_demo(selected: str, output_dir: Path) -> dict[str, Any]:
    """运行所选演示并汇总指标。"""
    features, regression_target, classification_target, series = synthetic_dataset()
    metrics: dict[str, Any] = {}

    def enabled(name: str) -> bool:
        return selected in {"all", name}

    if enabled("data"):
        demo_table = features.copy()
        demo_table["continuous_target"] = regression_target
        demo_table.loc[3, "feature_2"] = np.nan
        demo_table.to_csv(output_dir / "synthetic_demo_data.csv", index=False, encoding="utf-8-sig")
        metrics["data_audit"] = audit_dataframe(demo_table, output_dir)

    if enabled("regression"):
        metrics["regression"] = regression_baseline(features, regression_target, output_dir)

    if enabled("classification"):
        metrics["classification"] = classification_baseline(
            features, classification_target, output_dir
        )

    if enabled("clustering"):
        metrics["clustering"] = clustering_baseline(features, output_dir)

    if enabled("topsis"):
        alternatives = np.array(
            [
                [82, 12, 0.91, 6.0],
                [76, 9, 0.95, 7.5],
                [88, 15, 0.87, 5.0],
                [79, 10, 0.93, 6.8],
            ],
            dtype=float,
        )
        weights, scores = entropy_topsis(
            alternatives, benefit_flags=[True, False, True, False]
        )
        metrics["topsis"] = {
            "weights": weights,
            "scores": scores,
            "ranking_best_to_worst": np.argsort(-scores) + 1,
        }

    if enabled("optimization"):
        metrics["linear_program"] = linear_program_demo()

    if enabled("graph"):
        metrics["graph"] = graph_demo()

    if enabled("timeseries"):
        metrics["time_series"] = time_series_baseline(series, output_dir)

    if enabled("sensitivity"):
        def response(parameters: dict[str, float]) -> float:
            return parameters["a"] * 2.0**2 + parameters["b"] * 2.0 + parameters["c"]

        table = one_at_a_time_sensitivity(response, {"a": 2.0, "b": 1.5, "c": 5.0})
        table.to_csv(output_dir / "sensitivity_oat.csv", index=False, encoding="utf-8-sig")
        metrics["sensitivity"] = table.to_dict(orient="records")

    return metrics


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行 CUMCM 最小基线模板演示。")
    parser.add_argument(
        "--demo",
        default="all",
        choices=[
            "all",
            "data",
            "regression",
            "classification",
            "clustering",
            "topsis",
            "optimization",
            "graph",
            "timeseries",
            "sensitivity",
        ],
        help="选择要运行的模块。",
    )
    parser.add_argument("--out", default="demo_output", help="输出目录。")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    output_dir = make_output_dir(args.out)
    metrics = run_demo(args.demo, output_dir)
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(
        json.dumps(to_jsonable(metrics), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"完成：{args.demo}")
    print(f"结果目录：{output_dir.resolve()}")
    print(f"指标文件：{metrics_path.resolve()}")


if __name__ == "__main__":
    main()
