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



def _collect_envelope_data(
    data: dict[float, dict[float, dict[float, dict[str, float]]]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    altitude_map: dict[float, list[float]] = {}
    density_perturbation_map: dict[float, list[float]] = {}
    horizontal_wind_rss_map: dict[float, list[float]] = {}

    for lon_map in data.values():
        for alt_map in lon_map.values():
            for altitude, fields in alt_map.items():
                mean_density = fields.get("mean density")
                if mean_density is None:
                    continue

                altitude_map.setdefault(float(altitude), []).append(float(mean_density))

                ew_wind = fields.get("mean e w wind")
                ns_wind = fields.get("mean n s wind")
                if ew_wind is not None and ns_wind is not None:
                    horizontal_wind_rss_map.setdefault(float(altitude), []).append(
                        float(np.hypot(float(ew_wind), float(ns_wind)))
                    )

                density_perturbation_pct = fields.get("perturbation density")
                if density_perturbation_pct is not None:
                    density_perturbation_map.setdefault(float(altitude), []).append(float(density_perturbation_pct))

    if not altitude_map:
        raise ValueError("No 'mean density' entries were parsed from the supplied EarthGRAM files.")

    altitudes = np.array(sorted(altitude_map.keys()), dtype=float)
    density_min = np.empty_like(altitudes)
    density_max = np.empty_like(altitudes)
    density_avg = np.empty_like(altitudes)
    density_pct_diff_max = np.empty_like(altitudes)
    density_pct_diff_min = np.empty_like(altitudes)
    density_perturbation_max = np.full_like(altitudes, np.nan)
    horizontal_wind_rss_min = np.full_like(altitudes, np.nan)
    horizontal_wind_rss_max = np.full_like(altitudes, np.nan)
    horizontal_wind_rss_avg = np.full_like(altitudes, np.nan)

    for idx, altitude in enumerate(altitudes):
        density_values = np.array(altitude_map[float(altitude)], dtype=float)
        average_density = np.mean(density_values)

        density_min[idx] = np.min(density_values)
        density_max[idx] = np.max(density_values)
        density_avg[idx] = average_density

        if average_density == 0.0:
            density_pct_diff_max[idx] = np.nan
            density_pct_diff_min[idx] = np.nan
        else:
            density_pct_diff_max[idx] = 100.0 * (density_max[idx] - average_density) / average_density
            density_pct_diff_min[idx] = 100.0 * (density_min[idx] - average_density) / average_density

        perturbation_values = density_perturbation_map.get(float(altitude))
        if perturbation_values:
            density_perturbation_max[idx] = np.max(np.abs(np.asarray(perturbation_values, dtype=float)))

        horizontal_wind_rss_values = horizontal_wind_rss_map.get(float(altitude))
        if horizontal_wind_rss_values:
            horizontal_wind_rss_array = np.asarray(horizontal_wind_rss_values, dtype=float)
            horizontal_wind_rss_min[idx] = np.min(horizontal_wind_rss_array)
            horizontal_wind_rss_max[idx] = np.max(horizontal_wind_rss_array)
            horizontal_wind_rss_avg[idx] = np.mean(horizontal_wind_rss_array)

    return (
        altitudes,
        density_min,
        density_max,
        density_avg,
        density_pct_diff_max,
        density_pct_diff_min,
        density_perturbation_max,
        horizontal_wind_rss_min,
        horizontal_wind_rss_max,
        horizontal_wind_rss_avg,
    )


def plot_envelopes(
    input_dir: Path,
    pattern: str,
    output_prefix: str,
    prefer_filename_altitude: bool = False,
) -> tuple[Path, Path, Path, Path, Path]:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = read_earthgram_directory(
        input_dir=input_dir,
        pattern=pattern,
        prefer_filename_altitude=prefer_filename_altitude,
    )
    (
        altitudes,
        density_min,
        density_max,
        density_avg,
        density_pct_diff_max,
        density_pct_diff_min,
        density_perturbation_max,
        horizontal_wind_rss_min,
        horizontal_wind_rss_max,
        horizontal_wind_rss_avg,
    ) = _collect_envelope_data(data)

    density_path = input_dir / f"{output_prefix}_density_envelope.png"
    perturbation_path = input_dir / f"{output_prefix}_density_pct_envelope.png"
    maxmin_path = input_dir / f"{output_prefix}_density_pct_maxmin.png"
    perturbation_max_path = input_dir / f"{output_prefix}_density_perturbation_max.png"
    wind_rss_path = input_dir / f"{output_prefix}_horizontal_wind_rss_envelope.png"

    fig_density, ax_density = plt.subplots(1, 1, figsize=(6, 8), constrained_layout=True)
    ax_density.plot(density_min, altitudes, label="Min mean density", linewidth=2)
    ax_density.plot(density_avg, altitudes, label="Average mean density", linewidth=2, linestyle="--")
    ax_density.plot(density_max, altitudes, label="Max mean density", linewidth=2)
    ax_density.fill_betweenx(altitudes, density_min, density_max, alpha=0.25, label="Density envelope")
    ax_density.set_xscale("log")
    ax_density.set_xlabel(r"Mean Density $(\mathrm{kg}/\mathrm{m}^3)$")
    ax_density.set_ylabel(r"Altitude $(\mathrm{km})$")
    ax_density.set_title("EarthGRAM Mean-Density Envelope")
    ax_density.grid(True, which="both", linestyle=":")
    ax_density.legend(loc="best")
    # set ylim bottom to zero
    ax_density.set_ylim(bottom=0)
    fig_density.savefig(density_path, dpi=200)

    fig_perturbation, ax_perturbation = plt.subplots(1, 1, figsize=(4, 8), constrained_layout=True)
    ax_perturbation.plot(
        density_pct_diff_min,
        altitudes,
        label="Min vs. average mean density",
        linewidth=2,
        color="tab:blue",
    )
    ax_perturbation.plot(
        density_pct_diff_max,
        altitudes,
        label="Max vs. average mean density",
        linewidth=2,
        color="tab:red",
    )
    ax_perturbation.axvline(0.0, color="black", linewidth=1, linestyle="--")
    ax_perturbation.set_xlabel("Percent Difference from Average Mean Density (%)")
    ax_perturbation.set_ylabel(r"Altitude $(\mathrm{km})$")
    ax_perturbation.set_title("EarthGRAM Mean-Density Percent Envelope")
    ax_perturbation.grid(True, which="both", linestyle=":")
    ax_perturbation.legend(loc="best")
    ax_perturbation.set_ylim(bottom=0)
    fig_perturbation.savefig(perturbation_path, dpi=200)

    maxmin_density_pct = np.full_like(density_min, np.nan)
    valid_min = density_min != 0.0
    maxmin_density_pct[valid_min] = 100.0 * (density_max[valid_min] - density_min[valid_min]) / density_min[valid_min]

    fig_maxmin, ax_maxmin = plt.subplots(1, 1, figsize=(4, 8), constrained_layout=True)
    ax_maxmin.plot(maxmin_density_pct, altitudes, linewidth=2)
    ax_maxmin.set_xlim(left=0.0)
    ax_maxmin.set_xlabel(r"$(\rho_{\max} - \rho_{\min}) / \rho_{\min} $ (%)")
    ax_maxmin.set_ylabel(r"Altitude $(\mathrm{km})$")
    ax_maxmin.set_title("EarthGRAM Density Range Relative to Minimum")
    ax_maxmin.grid(True, which="both", linestyle=":")
    ax_maxmin.set_ylim(bottom=0)
    fig_maxmin.savefig(maxmin_path, dpi=200)

    fig_perturbation_max, ax_perturbation_max = plt.subplots(1, 1, figsize=(4, 8), constrained_layout=True)
    ax_perturbation_max.plot(density_perturbation_max, altitudes, linewidth=2)
    ax_perturbation_max.set_xlim(left=0.0)
    ax_perturbation_max.set_xlabel("Density Perturbation (%)")
    ax_perturbation_max.set_ylabel(r"Altitude $(\mathrm{km})$")
    ax_perturbation_max.set_title("EarthGRAM Maximum Density Perturbation")
    ax_perturbation_max.grid(True, which="both", linestyle=":")
    ax_perturbation_max.set_ylim(bottom=0)
    fig_perturbation_max.savefig(perturbation_max_path, dpi=200)

    fig_wind_rss, ax_wind_rss = plt.subplots(1, 1, figsize=(6, 8), constrained_layout=True)
    ax_wind_rss.plot(horizontal_wind_rss_min, altitudes, label="Min mean horizontal-wind RSS", linewidth=2)
    ax_wind_rss.plot(
        horizontal_wind_rss_avg,
        altitudes,
        label="Average mean horizontal-wind RSS",
        linewidth=2,
        linestyle="--",
    )
    ax_wind_rss.plot(horizontal_wind_rss_max, altitudes, label="Max mean horizontal-wind RSS", linewidth=2)
    ax_wind_rss.fill_betweenx(
        altitudes,
        horizontal_wind_rss_min,
        horizontal_wind_rss_max,
        alpha=0.25,
        label="Horizontal-wind RSS envelope",
    )
    ax_wind_rss.set_xlim(left=0.0)
    ax_wind_rss.set_xlabel(r"Mean Horizontal Wind RSS $(\mathrm{m}/\mathrm{s})$")
    ax_wind_rss.set_ylabel(r"Altitude $(\mathrm{km})$")
    ax_wind_rss.set_title("EarthGRAM Mean Horizontal-Wind RSS Envelope")
    ax_wind_rss.grid(True, which="both", linestyle=":")
    ax_wind_rss.legend(loc="best")
    ax_wind_rss.set_ylim(bottom=0)
    fig_wind_rss.savefig(wind_rss_path, dpi=200)

    return density_path, perturbation_path, maxmin_path, perturbation_max_path, wind_rss_path


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
    density_path, perturbation_path, maxmin_path, perturbation_max_path, wind_rss_path = plot_envelopes(
        input_dir=args.input_dir,
        pattern=args.pattern,
        output_prefix=args.output_prefix,
        prefer_filename_altitude=args.prefer_filename_altitude,
    )
    print(f"Saved envelope figure: {density_path}")
    print(f"Saved perturbation figure: {perturbation_path}")
    print(f"Saved max/min perturbation figure: {maxmin_path}")
    print(f"Saved max perturbation figure: {perturbation_max_path}")
    print(f"Saved horizontal-wind RSS figure: {wind_rss_path}")


if __name__ == "__main__":
    main()
