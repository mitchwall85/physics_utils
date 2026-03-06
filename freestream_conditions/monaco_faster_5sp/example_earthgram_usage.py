"""Example workflow: parse EarthGRAM outputs, pickle, and make contour plots."""

from __future__ import annotations

from pathlib import Path

try:
    from .earthgram_parser import read_earthgram_output
except ImportError:
    from earthgram_parser import read_earthgram_output


EarthgramData = dict[float, dict[float, dict[float, dict[str, float]]]]


def _normalize_longitude(longitude: float) -> float:
    """Wrap longitude to [-180, 180] so 180/-180 and 0/360 can be grouped."""
    wrapped = ((float(longitude) + 180.0) % 360.0) - 180.0
    if abs(wrapped + 180.0) < 1e-9:
        return 180.0
    if abs(wrapped) < 1e-9:
        return 0.0
    return wrapped


def _coalesce_longitudes(data: EarthgramData) -> EarthgramData:
    """Merge equivalent longitude bins (e.g. -180 and 180, 360 and 0)."""
    fixed: EarthgramData = {}
    for latitude, lon_map in data.items():
        for longitude, alt_map in lon_map.items():
            lon_key = _normalize_longitude(longitude)
            target = fixed.setdefault(float(latitude), {}).setdefault(float(lon_key), {})
            for altitude, fields in alt_map.items():
                target[float(altitude)] = fields
    return fixed


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
    import numpy as np

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    normalized_longitudes = tuple(_normalize_longitude(lon) for lon in longitudes)
    data = _coalesce_longitudes(data)

    x, y, mean_density, x_labels = _build_grids(data, normalized_longitudes, "mean density")
    _, _, std_density, _ = _build_grids(data, normalized_longitudes, "standard deviations density")

    if np.all(np.isnan(mean_density)):
        raise ValueError("No mean density data found for the selected longitudes.")

    positive_mean = mean_density[(~np.isnan(mean_density)) & (mean_density > 0.0)]
    if positive_mean.size == 0:
        raise ValueError("Mean density values are not positive; cannot use logarithmic color scale.")

    mean_levels = np.geomspace(positive_mean.min(), positive_mean.max(), 20)
    std_valid = std_density[~np.isnan(std_density)]
    std_levels = np.linspace(std_valid.min(), std_valid.max(), 20) if std_valid.size else 20

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)

    c1 = axes[0].contourf(x, y, mean_density, levels=mean_levels, norm=LogNorm())
    axes[0].contour(x, y, mean_density, levels=mean_levels[::2], colors="k", linewidths=0.5, alpha=0.55)
    axes[0].set_title(f"Mean Density (log scale), longitudes={normalized_longitudes}")
    axes[0].set_xlabel("Latitude stitched by longitude (all 0° points, then 180° points)")
    axes[0].set_ylabel("Altitude (km)")
    fig.colorbar(c1, ax=axes[0], label="Mean Density (kg/m^3)")

    c2 = axes[1].contourf(x, y, std_density, levels=std_levels)
    axes[1].contour(x, y, std_density, levels=10, colors="k", linewidths=0.5, alpha=0.55)
    axes[1].set_title(f"Standard Deviation Density (%), longitudes={normalized_longitudes}")
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
    earthgram_files: dict[float, str] = {
        75.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_75km_LIST.md",
        85.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_85km_LIST.md",
        95.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_95km_LIST.md",
        105.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_105km_LIST.md",
        115.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_115km_LIST.md",
        125.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_125km_LIST.md",
        135.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_135km_LIST.md",
        145.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_145km_LIST.md",
    }

    data = _coalesce_longitudes(read_earthgram_output(earthgram_files, pickle_name="earthgram_records.pkl"))

    for longitude in longitude_order:
        normalized_lon = _normalize_longitude(longitude)
        if not any(normalized_lon in lon_map for lon_map in data.values()):
            raise ValueError(f"Longitude {normalized_lon} is not present in parsed data.")

    print(f"Parsed {len(data)} latitude entries.")
    sample_lat = sorted(data.keys())[-1]
    sample_lon = _normalize_longitude(longitude_order[0])
    sample_alt = sorted(data[sample_lat][sample_lon].keys())[0]
    sample_density = data[sample_lat][sample_lon][sample_alt].get("mean density")
    print(f"Example query -> data[{sample_lat}][{sample_lon}][{sample_alt}]['mean density'] = {sample_density}")

    plot_density_contours(data, longitudes=longitude_order)


if __name__ == "__main__":
    main()
