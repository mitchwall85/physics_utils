"""Example workflow: parse EarthGRAM output, pickle it, and make contour plots."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

# Use a headless backend so this script works on servers/CLI environments.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from earthgram_parser import read_earthgram_output


def _build_grids(
    data: dict[float, dict[float, dict[float, dict[str, float]]]],
    longitude: float,
    value_key: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    latitudes = sorted(data.keys())
    altitudes = sorted({alt for lat in latitudes for alt in data[lat].get(longitude, {}).keys()})

    z = np.full((len(altitudes), len(latitudes)), np.nan)

    for lat_idx, lat in enumerate(latitudes):
        lon_slice = data[lat].get(longitude, {})
        for alt_idx, alt in enumerate(altitudes):
            if alt not in lon_slice:
                continue
            value = lon_slice[alt].get(value_key)
            if value is None:
                continue
            z[alt_idx, lat_idx] = float(value)

    x, y = np.meshgrid(latitudes, altitudes)
    return x, y, z


def plot_density_contours(
    data: dict[float, dict[float, dict[float, dict[str, float]]]],
    longitude: float,
) -> None:
    x, y, mean_density = _build_grids(data, longitude, "mean density")
    _, _, std_density = _build_grids(data, longitude, "standard deviations density")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)

    c1 = axes[0].contourf(x, y, mean_density, levels=20)
    axes[0].set_title(f"Mean Density at Longitude {longitude} deg")
    axes[0].set_xlabel("Latitude (deg)")
    axes[0].set_ylabel("Altitude (km)")
    fig.colorbar(c1, ax=axes[0], label="Mean Density (kg/m^3)")

    c2 = axes[1].contourf(x, y, std_density, levels=20)
    axes[1].set_title(f"Standard Deviation Density (%) at Longitude {longitude} deg")
    axes[1].set_xlabel("Latitude (deg)")
    axes[1].set_ylabel("Altitude (km)")
    fig.colorbar(c2, ax=axes[1], label="Standard Deviation Density (%)")

    output_path = Path(f"earthgram_density_contours_lon_{longitude:g}.png")
    fig.savefig(output_path, dpi=200)
    print(f"Saved contour figure: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse EarthGRAM output and make contour plots.")
    parser.add_argument("earthgram_file", help="Path to EarthGRAM text output file.")
    parser.add_argument("--longitude", type=float, required=True, help="Longitude slice for contour plots.")
    parser.add_argument(
        "--pickle-name",
        default="earthgram_records.pkl",
        help="Name of the output pickle file in the same directory as the text file.",
    )
    args = parser.parse_args()

    data = read_earthgram_output(args.earthgram_file, pickle_name=args.pickle_name)

    longitude = args.longitude
    if not any(longitude in lon_map for lon_map in data.values()):
        raise ValueError(f"Longitude {longitude} is not present in parsed data.")

    print(f"Parsed {len(data)} latitude entries.")

    # Show a robust example query from the first available lat/lon/alt point.
    sample_lat = sorted(data.keys())[0]
    sample_altitudes = sorted(data[sample_lat][longitude].keys())
    sample_alt = sample_altitudes[0]
    sample_mean_density = data[sample_lat][longitude][sample_alt].get("mean density")
    print(
        "Example query -> "
        f"data[{sample_lat}][{longitude}][{sample_alt}]['mean density'] = {sample_mean_density}"
    )

    plot_density_contours(data, longitude)


if __name__ == "__main__":
    main()
