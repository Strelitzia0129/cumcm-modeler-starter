# CUMCM Modeler Starter

[English](README.en.md) | 简体中文

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](pyproject.toml)
[![Docs](https://img.shields.io/badge/docs-offline%20HTML-21876f.svg)](docs/index.html)

面向全国大学生数学建模竞赛建模手的开源入门与赛时速查工具包。项目把“题目输出是什么”作为算法选择入口，提供算法导航、训练计划、权威资料目录、可运行基线和模型验证清单。

> 本项目是非官方社区项目，与全国大学生数学建模竞赛组织委员会、中国工业与应用数学学会及相关主办单位无隶属或背书关系。比赛规则可能变化，请始终以当届官网为准。

## 项目内容

- 21 张可搜索算法卡：识别信号、最低基线、升级条件、验证方法与常见误用。
- 34 条官方或权威资料入口，不镜像第三方受版权保护内容。
- 30 天零基础冲刺计划和赛题开局协议。
- Python 基线：TOPSIS、敏感性分析，以及回归、分类、聚类、优化、图论和时序示例。
- 2026 年 AI 工具使用留痕模板。
- 自动测试、代码检查和 GitHub Pages 部署工作流。

## 立即使用

不安装任何软件也可以打开 [离线算法导航](docs/index.html)。

最小 Python 安装只需要 NumPy 和 pandas：

```bash
python -m venv .venv
python -m pip install -e .
cumcm-starter check-env
cumcm-starter demo --out demo_output
```

需要运行完整建模示例时：

```bash
python -m pip install -e ".[modeling]"
python examples/baseline_demos.py --demo all --out demo_output/full
```

Windows PowerShell 激活虚拟环境的命令是：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 算法选择原则

1. 先判断子问题是否真的需要建模；确定性公式代入不强行套模型。
2. 根据输出区分预测、分类、评价、优化、机理、统计或网络问题。
3. 先做可解释、可验证的基线，再根据失败证据升级复杂模型。
4. 预测必须样本外验证，优化必须检查可行性，机理模型必须检查量纲和边界。
5. 所有核心结论都应包含敏感性、稳健性或误差证据。

## 文档

- [算法导航](docs/index.html)
- [30 天冲刺计划](docs/30-day-sprint.md)
- [资料来源目录](docs/sources.csv)
- [AI 工具使用详情模板](docs/ai-usage-log-template.md)
- [免责声明](DISCLAIMER.md)
- [路线图](ROADMAP.md)
- [开源发布说明](docs/open-source-release.md)

## 开发与测试

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python scripts/verify_repository.py
ruff check src tests scripts examples
```

提交算法或资料前，请阅读 [贡献指南](CONTRIBUTING.md)。算法卡必须写清适用边界、最低基线、验证方法和来源，不能只添加算法名称。

## 开源与引用

原创代码和文档按 [MIT License](LICENSE) 发布。第三方资料仍归各自权利人所有，本项目只提供链接与简要元数据，详见 [第三方说明](THIRD_PARTY_NOTICES.md)。

学术或教学使用可按 [CITATION.cff](CITATION.cff) 引用本项目。
