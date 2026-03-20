from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CONVERGENCE_FILENAME = "convergence.plt"
TIME_STEP_KEY = "time step number"
PLOT_KEYS = ["particles", "collisions", "global convergence level"]


def read_convergence_file(file_path: str | Path) -> dict[str, np.ndarray]:
    """Read a ``convergence.plt`` file into a dictionary keyed by variable name."""
    path = Path(file_path)
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    if not lines:
        raise ValueError(f"Convergence file is empty: {path}")

    variables_line = next((line for line in lines if line.startswith("VARIABLES")), None)
    if variables_line is None:
        raise ValueError(f"Missing VARIABLES header in {path}")

    variable_names = [token.strip().strip('"') for token in variables_line.split("=", maxsplit=1)[1].split(",")]
    data_start = next((index + 1 for index, line in enumerate(lines) if line == "ZONE"), None)
    if data_start is None:
        raise ValueError(f"Missing ZONE header in {path}")

    columns: dict[str, list[float]] = {name: [] for name in variable_names}
    for line in lines[data_start:]:
        values = line.split()
        if len(values) != len(variable_names):
            raise ValueError(
                f"Expected {len(variable_names)} columns in {path}, found {len(values)} in line: {line}"
            )

        for name, value in zip(variable_names, values):
            columns[name].append(float(value))

    return {name: np.asarray(values, dtype=float) for name, values in columns.items()}



def main() -> None:
    dirs = {
        # "case_name": "/path/to/directory/containing/convergence.plt",
        # "baseline": "/path/to/baseline/run",
        # "refined_mesh": "/path/to/refined_mesh/run",
    }
    output_path = Path("convergence_histories.png")

    if not dirs:
        raise ValueError(
            "Populate the `dirs` dictionary in plot_convergence.py with case names and directories before running."
        )

    fig, axes = plt.subplots(len(PLOT_KEYS), 1, figsize=(10, 10), sharex=True, constrained_layout=True)

    for case_name, directory in dirs.items():
        file_path = Path(directory) / CONVERGENCE_FILENAME
        convergence_data = read_convergence_file(file_path)
        time_steps = convergence_data[TIME_STEP_KEY]

        for axis, variable_name in zip(axes, PLOT_KEYS):
            values = convergence_data[variable_name]
            positive_values = np.where(values > 0.0, values, np.nan)
            axis.plot(time_steps, positive_values, label=case_name)
            axis.set_ylabel(variable_name)
            axis.set_yscale("log")
            axis.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)

    axes[0].set_title("Convergence history comparison")
    axes[-1].set_xlabel(TIME_STEP_KEY)
    axes[0].legend()
    fig.savefig(output_path, dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
