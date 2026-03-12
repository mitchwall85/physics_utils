"""Plot EarthGRAM density envelopes across many output files in one directory."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import numpy as np

try:
    from .earthgram_parser import read_earthgram_directory
except ImportError:
    from earthgram_parser import read_earthgram_directory


POSSIBLE_DENSITY_PERTURBATION_KEYS = (
    "density perturbation",
    "density perturbation percent",
    "density perturbation ",
    "standard deviations density",
    "sigma rho rho",
)


def _collect_envelope_data(data: dict[float, dict[float, dict[float, dict[str, float]]]]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    altitude_map: dict[float, list[tuple[float, float | None]]] = {}

    for lon_map in data.values():
        for alt_map in lon_map.values():
            for altitude, fields in alt_map.items():
                mean_density = fields.get("mean density")
                if mean_density is None:
                    continue

                perturbation = None
                for key in POSSIBLE_DENSITY_PERTURBATION_KEYS:
                    if key in fields and fields[key] is not None:
                        perturbation = float(fields[key])
                        break

                altitude_map.setdefault(float(altitude), []).append((float(mean_density), perturbation))

    if not altitude_map:
        raise ValueError("No 'mean density' entries were parsed from the supplied EarthGRAM files.")

    altitudes = np.array(sorted(altitude_map.keys()), dtype=float)
    density_min = np.empty_like(altitudes)
    density_max = np.empty_like(altitudes)
    perturbation_max = np.empty_like(altitudes)

    for idx, altitude in enumerate(altitudes):
        values = altitude_map[float(altitude)]
        density_values = np.array([entry[0] for entry in values], dtype=float)
        perturbation_values = np.array(
            [abs(entry[1]) for entry in values if entry[1] is not None],
            dtype=float,
        )

        density_min[idx] = np.min(density_values)
        density_max[idx] = np.max(density_values)
        perturbation_max[idx] = np.max(perturbation_values) if perturbation_values.size else np.nan

    return altitudes, density_min, density_max, perturbation_max


def plot_envelopes(
    input_dir: Path,
    pattern: str,
    output_prefix: str,
    prefer_filename_altitude: bool = False,
) -> tuple[Path, Path]:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = read_earthgram_directory(
        input_dir=input_dir,
        pattern=pattern,
        prefer_filename_altitude=prefer_filename_altitude,
    )
    altitudes, density_min, density_max, perturbation_max = _collect_envelope_data(data)

    density_path = input_dir / f"{output_prefix}_density_envelope.png"
    perturbation_path = input_dir / f"{output_prefix}_perturbation_max.png"

    fig_density, ax_density = plt.subplots(1, 1, figsize=(6, 8), constrained_layout=True)
    ax_density.plot(density_min, altitudes, label="Min mean density", linewidth=2)
    ax_density.plot(density_max, altitudes, label="Max mean density", linewidth=2)
    ax_density.fill_betweenx(altitudes, density_min, density_max, alpha=0.25, label="Density envelope")
    ax_density.set_xscale("log")
    ax_density.set_xlabel(r"Mean Density $(\mathrm{kg}/\mathrm{m}^3)$")
    ax_density.set_ylabel(r"Altitude $(\mathrm{km})$")
    ax_density.set_title("EarthGRAM Mean-Density Envelope")
    ax_density.grid(True, which="both", linestyle=":")
    ax_density.legend(loc="best")
    fig_density.savefig(density_path, dpi=200)

    fig_perturbation, ax_perturbation = plt.subplots(1, 1, figsize=(6, 8), constrained_layout=True)
    ax_perturbation.plot(perturbation_max, altitudes, label="Max density perturbation", linewidth=2, color="tab:red")
    ax_perturbation.set_xlabel("Max Density Perturbation")
    ax_perturbation.set_ylabel(r"Altitude $(\mathrm{km})$")
    ax_perturbation.set_title("EarthGRAM Max Density Perturbation by Altitude")
    ax_perturbation.grid(True, which="both", linestyle=":")
    ax_perturbation.legend(loc="best")
    fig_perturbation.savefig(perturbation_path, dpi=200)

    return density_path, perturbation_path


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read all EarthGRAM outputs in a directory and plot altitude envelopes.",
    )
    parser.add_argument("input_dir", type=Path, help="Directory containing EarthGRAM output files.")
    parser.add_argument(
        "--pattern",
        default="*.md",
        help="Glob pattern for EarthGRAM output files inside input_dir (default: *.md).",
    )
    parser.add_argument(
        "--output-prefix",
        default="earthgram",
        help="Prefix for output figure names (default: earthgram).",
    )
    parser.add_argument(
        "--prefer-filename-altitude",
        action="store_true",
        help=(
            "Infer/override altitude from filenames instead of using altitude from "
            "each EarthGRAM record. Use only when files are single-altitude slices."
        ),
    )
    return parser


def main() -> None:
    args = _build_arg_parser().parse_args()
    density_path, perturbation_path = plot_envelopes(
        input_dir=args.input_dir,
        pattern=args.pattern,
        output_prefix=args.output_prefix,
        prefer_filename_altitude=args.prefer_filename_altitude,
    )
    print(f"Saved envelope figure: {density_path}")
    print(f"Saved perturbation figure: {perturbation_path}")


if __name__ == "__main__":
    main()
