# CUMCM Modeler Starter

[简体中文](README.md) | English

An open-source algorithm navigator, validation checklist, training roadmap,
and reproducible Python baseline toolkit for mathematical modeling contestants.

> This is an unofficial community project. It is not affiliated with or
> endorsed by the CUMCM organizing committee, CSIAM, any regional committee,
> university, or course provider. Always follow the official rules for the
> current competition year.

## What is included

- A searchable offline guide with 21 algorithm cards.
- 34 official or authoritative learning links with access and license notes.
- A 30-day beginner sprint and contest-start protocol.
- A lightweight CLI with TOPSIS and sensitivity-analysis baselines.
- Extended examples for regression, classification, clustering, optimization,
  graph problems, and time-series validation.
- Tests, repository audits, GitHub Actions CI, and GitHub Pages deployment.

## Quick start

Open [the offline algorithm guide](docs/index.html), or install the minimal CLI:

```bash
python -m venv .venv
python -m pip install -e .
cumcm-starter check-env
cumcm-starter demo --out demo_output
```

For the extended modeling examples:

```bash
python -m pip install -e ".[modeling]"
python examples/baseline_demos.py --demo all --out demo_output/full
```

## Modeling principles

1. Identify the requested output before naming an algorithm.
2. Start with an interpretable, verifiable baseline.
3. Upgrade only when residuals, constraints, nonlinearities, or instability
   provide evidence that the baseline is insufficient.
4. Use out-of-sample validation for prediction, feasibility checks for
   optimization, and dimensional and boundary checks for mechanistic models.
5. Report sensitivity, uncertainty, and limitations for every major result.

## Contributing and license

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a new algorithm card or
source. Original repository content is released under the [MIT License](LICENSE).
Third-party content remains the property of its respective rights holders; the
repository stores links and short metadata rather than copies.

