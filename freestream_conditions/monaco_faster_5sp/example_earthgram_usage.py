"""Example workflow: parse EarthGRAM outputs, pickle, and make contour plots."""

from __future__ import annotations

from pathlib import Path

try:
    from .earthgram_parser import read_earthgram_output
except ImportError:
    from earthgram_parser import read_earthgram_output


EarthgramData = dict[float, dict[float, dict[float, dict[str, float]]]]


def _build_grids(
    data: EarthgramData,
    longitude: float,
    value_key: str,
) -> tuple[object, object, object]:
    import numpy as np

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


def plot_density_contours(data: EarthgramData, longitude: float) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

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
    longitude = 0.0

    # Input format: altitude (km) -> EarthGRAM file for that altitude.
    earthgram_files = {
        70.0: "conditions_gram_mass_70.txt",
        80.0: "conditions_gram_mass_80.txt",
        85.0: "conditions_gram_mass_85.txt",
        110.0: "conditions_gram_mass_110.txt",
    }

    data = read_earthgram_output(earthgram_files, pickle_name="earthgram_records.pkl")

    if not any(longitude in lon_map for lon_map in data.values()):
        raise ValueError(f"Longitude {longitude} is not present in parsed data.")

    print(f"Parsed {len(data)} latitude entries.")
    sample_lat = sorted(data.keys())[0]
    sample_alt = sorted(data[sample_lat][longitude].keys())[0]
    sample_density = data[sample_lat][longitude][sample_alt].get("mean density")
    print(f"Example query -> data[{sample_lat}][{longitude}][{sample_alt}]['mean density'] = {sample_density}")

    plot_density_contours(data, longitude)


if __name__ == "__main__":
    main()
