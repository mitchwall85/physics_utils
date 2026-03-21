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
    variables_index = lines.index(variables_line)
    data_lines = lines[variables_index + 1 :]
    if data_lines and data_lines[0] == "ZONE":
        data_lines = data_lines[1:]
    if not data_lines:
        raise ValueError(f"Missing convergence data rows in {path}")

    columns: dict[str, list[float]] = {name: [] for name in variable_names}
    for line in data_lines:
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
        "1000": "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/dakota-monaco/90km_16kms_33_params_v3/monaco_template_burt_conv_1000/",
        "2500": "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/dakota-monaco/90km_16kms_33_params_v3/monaco_template_burt_conv_2500/",
        "5000": "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/dakota-monaco/90km_16kms_33_params_v3/monaco_template_burt_conv_5000/",
        "10000": "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/dakota-monaco/90km_16kms_33_params_v3/monaco_template_burt_conv_10000/"
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
