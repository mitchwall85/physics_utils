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
    longitudes: tuple[float, ...],
    value_key: str,
) -> tuple[object, object, object, list[str]]:
    import numpy as np

    latitudes = sorted(data.keys())
    altitudes = sorted(
        {
            alt
            for lat in latitudes
            for longitude in longitudes
            for alt in data[lat].get(longitude, {}).keys()
        }
    )

    x_pairs: list[tuple[float, float]] = []
    x_labels: list[str] = []
    for longitude in longitudes:
        for lat in latitudes:
            if longitude in data[lat]:
                x_pairs.append((lat, longitude))
                x_labels.append(f"{lat:g}° @ {longitude:g}°")

    z = np.full((len(altitudes), len(x_pairs)), np.nan)

    for x_idx, (lat, longitude) in enumerate(x_pairs):
        lon_slice = data[lat].get(longitude, {})
        for alt_idx, alt in enumerate(altitudes):
            if alt not in lon_slice:
                continue
            value = lon_slice[alt].get(value_key)
            if value is None:
                continue
            z[alt_idx, x_idx] = float(value)

    x_positions = np.arange(len(x_pairs), dtype=float)
    x, y = np.meshgrid(x_positions, altitudes)
    return x, y, z, x_labels


def plot_density_contours(data: EarthgramData, longitudes: tuple[float, ...] = (0.0, 180.0)) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x, y, mean_density, x_labels = _build_grids(data, longitudes, "mean density")
    _, _, std_density, _ = _build_grids(data, longitudes, "standard deviations density")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)

    c1 = axes[0].contourf(x, y, mean_density, levels=20)
    axes[0].set_title(f"Mean Density, longitudes={longitudes}")
    axes[0].set_xlabel("Latitude stitched by longitude (all 0° points, then 180° points)")
    axes[0].set_ylabel("Altitude (km)")
    fig.colorbar(c1, ax=axes[0], label="Mean Density (kg/m^3)")

    c2 = axes[1].contourf(x, y, std_density, levels=20)
    axes[1].set_title(f"Standard Deviation Density (%), longitudes={longitudes}")
    axes[1].set_xlabel("Latitude stitched by longitude (all 0° points, then 180° points)")
    axes[1].set_ylabel("Altitude (km)")
    fig.colorbar(c2, ax=axes[1], label="Standard Deviation Density (%)")

    # Keep tick count readable while preserving the stitched ordering.
    tick_step = max(1, len(x_labels) // 12)
    tick_positions = list(range(0, len(x_labels), tick_step))
    for ax in axes:
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([x_labels[idx] for idx in tick_positions], rotation=45, ha="right")

    output_path = Path("earthgram_density_contours_lon_0_then_180.png")
    fig.savefig(output_path, dpi=200)
    print(f"Saved contour figure: {output_path}")


def main() -> None:
    longitude_order = (0.0, 180.0)

    # Input format: altitude (km) -> EarthGRAM file for that altitude.
    earthgram_files = {
        70.0: "conditions_gram_mass_70.txt",
        80.0: "conditions_gram_mass_80.txt",
        85.0: "conditions_gram_mass_85.txt",
        110.0: "conditions_gram_mass_110.txt",
    }

    data = read_earthgram_output(earthgram_files, pickle_name="earthgram_records.pkl")

    for longitude in longitude_order:
        if not any(longitude in lon_map for lon_map in data.values()):
            raise ValueError(f"Longitude {longitude} is not present in parsed data.")

    print(f"Parsed {len(data)} latitude entries.")
    sample_lat = sorted(data.keys())[0]
    sample_alt = sorted(data[sample_lat][longitude_order[0]].keys())[0]
    sample_density = data[sample_lat][longitude_order[0]][sample_alt].get("mean density")
    print(f"Example query -> data[{sample_lat}][{longitude_order[0]}][{sample_alt}]['mean density'] = {sample_density}")

    plot_density_contours(data, longitudes=longitude_order)


if __name__ == "__main__":
    main()
