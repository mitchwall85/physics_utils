"""Plot reference-length envelope using Monaco 5-species mean-free-path function.

This script uses ``mfp_altitude_5sp_monaco`` to compute mean free path across altitude,
then builds a 3-y-axis plot versus reference length:
- altitude,
- total number density,
- Knudsen number.

The Kn=1 curve corresponds to ``L_ref = mfp`` for each altitude.
"""

from __future__ import annotations

from pathlib import Path
import argparse

import numpy as np
import matplotlib

try:
    from physics_utils.freestream_conditions.monaco_faster_5sp import mfp_altitude_fun
except ImportError:
    import mfp_altitude_fun


def _load_conditions_table(path: Path) -> np.ndarray:
    data = np.genfromtxt(path, delimiter=",", skip_header=1)
    if data.ndim != 2 or data.shape[1] < 6:
        raise ValueError(f"Unexpected table format in {path}")
    return data


def _interp_species_densities(data: np.ndarray, altitudes_km: np.ndarray) -> np.ndarray:
    table_alt = data[:, 0]
    # columns: altitude, T, N2, O2, N, O
    n_total = np.zeros_like(altitudes_km)
    for col in (2, 3, 4, 5):
        n_total += np.interp(altitudes_km, table_alt, data[:, col])
    return n_total


def _patch_mfp_source_with_local_table(data: np.ndarray) -> None:
    """Patch dependency so mfp_altitude_5sp_monaco can run with repo-local data."""

    def _local_calc_inflow_mass_5sp(height: float, return_labels: bool = False):
        t_val = float(np.interp(height, data[:, 0], data[:, 1]))
        n2 = float(np.interp(height, data[:, 0], data[:, 2]))
        o2 = float(np.interp(height, data[:, 0], data[:, 3]))
        n = float(np.interp(height, data[:, 0], data[:, 4]))
        o = float(np.interp(height, data[:, 0], data[:, 5]))
        values = np.array([t_val, n2, o2, n, o])
        if return_labels:
            return values, ["T", "N_2", "O_2", "N", "O"]
        return values

    # mfp_altitude_5sp_monaco resolves calc_inflow_mass_5sp from module global scope.
    mfp_altitude_fun.calc_inflow_mass_5sp = _local_calc_inflow_mass_5sp


def make_plot(output: Path, alt_min: float, alt_max: float, n_points: int) -> Path:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    this_dir = Path(__file__).resolve().parent
    table_path = this_dir / "conditions_gram_mass.txt"
    table = _load_conditions_table(table_path)

    altitudes = np.linspace(alt_min, alt_max, n_points)
    _patch_mfp_source_with_local_table(table)

    mfp_vals = np.array([mfp_altitude_fun.mfp_altitude_5sp_monaco(float(h)) for h in altitudes])
    n_tot = _interp_species_densities(table, altitudes)

    # Reference-length curve for Kn=1 is simply L_ref = mfp.
    l_ref_kn1 = mfp_vals
    kn_curve = mfp_vals / l_ref_kn1

    fig, ax_alt = plt.subplots(figsize=(9, 6), constrained_layout=True)
    ax_den = ax_alt.twinx()
    ax_kn = ax_alt.twinx()

    # Offset third y-axis.
    ax_kn.spines["right"].set_position(("outward", 70))

    l1, = ax_alt.plot(l_ref_kn1, altitudes, color="tab:blue", linewidth=2, label="Altitude (Kn=1)")
    l2, = ax_den.plot(l_ref_kn1, n_tot, color="tab:green", linewidth=2, linestyle="--", label="Total number density")
    l3, = ax_kn.plot(l_ref_kn1, kn_curve, color="tab:red", linewidth=2, label="Knudsen number")

    # Explicit Kn=1 reference curve.
    l4 = ax_kn.axhline(1.0, color="tab:red", linestyle=":", linewidth=1.5, label="Kn = 1")

    ax_alt.set_xscale("log")
    ax_den.set_yscale("log")

    ax_alt.set_xlabel("Reference length, L_ref (m)")
    ax_alt.set_ylabel("Altitude (km)", color="tab:blue")
    ax_den.set_ylabel("Total number density (1/m^3)", color="tab:green")
    ax_kn.set_ylabel("Knudsen number", color="tab:red")

    ax_alt.tick_params(axis="y", labelcolor="tab:blue")
    ax_den.tick_params(axis="y", labelcolor="tab:green")
    ax_kn.tick_params(axis="y", labelcolor="tab:red")

    ax_alt.grid(True, which="both", linestyle=":", alpha=0.5)
    ax_alt.set_title("5-Species Monaco Mean Free Path Envelope (Kn=1)")

    handles = [l1, l2, l3, l4]
    labels = [h.get_label() for h in handles]
    ax_alt.legend(handles, labels, loc="best")

    fig.savefig(output, dpi=200)
    return output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot Monaco 5sp reference-length envelope with three y-axes.")
    parser.add_argument("--alt-min", type=float, default=50.0, help="Minimum altitude in km.")
    parser.add_argument("--alt-max", type=float, default=200.0, help="Maximum altitude in km.")
    parser.add_argument("--n-points", type=int, default=400, help="Number of altitude samples.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("plot_mpc_envelop.png"),
        help="Output figure path.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    out = make_plot(args.output, args.alt_min, args.alt_max, args.n_points)
    print(f"Saved figure: {out}")


if __name__ == "__main__":
    main()
