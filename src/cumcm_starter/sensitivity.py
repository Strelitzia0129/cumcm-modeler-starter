"""Simple sensitivity-analysis baselines."""

from __future__ import annotations

from collections.abc import Callable, Mapping

import numpy as np
import pandas as pd


def one_at_a_time_sensitivity(
    model: Callable[[dict[str, float]], float],
    base_parameters: Mapping[str, float],
    relative_change: float = 0.10,
) -> pd.DataFrame:
    """Perturb each parameter up and down while holding the others fixed.

    OAT is useful as a first diagnostic. It does not measure interactions and
    should be upgraded to Morris or Sobol analysis when interactions matter.
    """
    if not base_parameters:
        raise ValueError("base_parameters cannot be empty")
    if not 0 < relative_change < 1:
        raise ValueError("relative_change must be between 0 and 1")

    parameters = {name: float(value) for name, value in base_parameters.items()}
    if not all(np.isfinite(value) for value in parameters.values()):
        raise ValueError("base parameters must be finite")

    base_output = float(model(dict(parameters)))
    if not np.isfinite(base_output):
        raise ValueError("model returned a non-finite baseline output")

    rows: list[dict[str, float | str]] = []
    for name, base_value in parameters.items():
        for direction in (-1.0, 1.0):
            changed = dict(parameters)
            changed[name] = base_value * (1.0 + direction * relative_change)
            output = float(model(changed))
            if not np.isfinite(output):
                raise ValueError(f"model returned a non-finite output for parameter {name}")
            rows.append(
                {
                    "parameter": name,
                    "parameter_change": direction * relative_change,
                    "parameter_value": changed[name],
                    "output": output,
                    "absolute_output_change": output - base_output,
                    "relative_output_change": (
                        (output - base_output) / abs(base_output)
                        if base_output != 0
                        else np.nan
                    ),
                }
            )
    return pd.DataFrame(rows)

