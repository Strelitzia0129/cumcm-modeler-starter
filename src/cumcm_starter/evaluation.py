"""Transparent multi-criteria evaluation baselines."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray


def entropy_topsis(
    decision_matrix: NDArray[np.floating] | Sequence[Sequence[float]],
    benefit_flags: Sequence[bool],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return entropy weights and TOPSIS scores.

    Parameters
    ----------
    decision_matrix:
        Rows are alternatives and columns are indicators.
    benefit_flags:
        ``True`` means a larger indicator is better; ``False`` means smaller
        is better.

    Notes
    -----
    This is a transparent baseline, not a universal ranking method. A contest
    solution should justify indicator definitions and test ranking sensitivity
    to normalization and weight perturbations.
    """
    matrix = np.asarray(decision_matrix, dtype=float)
    flags = tuple(benefit_flags)
    if matrix.ndim != 2:
        raise ValueError("decision_matrix must be two-dimensional")
    if matrix.shape[0] < 2 or matrix.shape[1] < 1:
        raise ValueError("at least two alternatives and one indicator are required")
    if matrix.shape[1] != len(flags):
        raise ValueError("benefit_flags length must match the number of indicators")
    if not np.isfinite(matrix).all():
        raise ValueError("decision_matrix cannot contain missing or infinite values")

    column_min = matrix.min(axis=0)
    column_range = matrix.max(axis=0) - column_min
    normalized = (matrix - column_min) / np.where(column_range == 0, 1.0, column_range)
    for column, is_benefit in enumerate(flags):
        if not is_benefit:
            normalized[:, column] = 1.0 - normalized[:, column]

    epsilon = np.finfo(float).eps
    column_sums = normalized.sum(axis=0)
    proportions = normalized / np.where(column_sums == 0, 1.0, column_sums)
    entropy_scale = 1.0 / np.log(matrix.shape[0])
    entropy = -entropy_scale * np.sum(
        np.where(proportions > 0, proportions * np.log(proportions + epsilon), 0.0),
        axis=0,
    )
    information = np.where(
        column_range == 0,
        0.0,
        np.clip(1.0 - entropy, 0.0, None),
    )
    weights = (
        information / information.sum()
        if information.sum() > epsilon
        else np.full(matrix.shape[1], 1.0 / matrix.shape[1])
    )

    weighted = normalized * weights
    ideal_best = weighted.max(axis=0)
    ideal_worst = weighted.min(axis=0)
    distance_best = np.linalg.norm(weighted - ideal_best, axis=1)
    distance_worst = np.linalg.norm(weighted - ideal_worst, axis=1)
    scores = distance_worst / (distance_best + distance_worst + epsilon)
    return weights.astype(np.float64), scores.astype(np.float64)
