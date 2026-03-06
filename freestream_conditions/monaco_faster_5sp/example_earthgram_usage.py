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
) -> tuple[object, object, object, list[tuple[float, float]], list[str]]:
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

    ordering: list[tuple[float, tuple[float, float]]] = []
    for lat in latitudes:
        for longitude in longitudes:
            lon_slice = data[lat].get(longitude, {})
            if not lon_slice:
                continue
            record_numbers = [
                fields.get("record number")
                for fields in lon_slice.values()
                if fields.get("record number") is not None
            ]
            record_order = min(float(rec) for rec in record_numbers) if record_numbers else float("inf")
            ordering.append((record_order, (lat, longitude)))

    ordering.sort(key=lambda item: item[0])
    x_pairs: list[tuple[float, float]] = [pair for _, pair in ordering]
    x_labels: list[str] = [f"({lat:g}\N{DEGREE SIGN}, {longitude:g}\N{DEGREE SIGN})" for lat, longitude in x_pairs]

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
    return x, y, z, x_pairs, x_labels


def _format_sweep_label(latitude: float, longitude: float, tolerance: float = 1e-6) -> str:
    if abs(latitude - 90.0) <= tolerance and abs(longitude - 0.0) <= tolerance:
        return "North Pole"
    if abs(latitude + 90.0) <= tolerance and abs(longitude - 180.0) <= tolerance:
        return "South Pole"
    if abs(latitude) <= tolerance and (abs(longitude - 0.0) <= tolerance or abs(longitude - 180.0) <= tolerance):
        return "Equator"
    return f"({latitude:g}\N{DEGREE SIGN}, {longitude:g}\N{DEGREE SIGN})"


def _is_30_degree_multiple(latitude: float, tolerance: float = 1e-6) -> bool:
    return abs(latitude / 30.0 - round(latitude / 30.0)) <= tolerance


def _build_tick_positions(
    x_pairs: list[tuple[float, float]],
    preferred_longitude: float,
) -> list[int]:
    tick_positions = [
        idx
        for idx, (lat, lon) in enumerate(x_pairs)
        if abs(lon - preferred_longitude) <= 1e-6 and _is_30_degree_multiple(lat)
    ]

    if not tick_positions:
        tick_positions = [idx for idx, (lat, _) in enumerate(x_pairs) if _is_30_degree_multiple(lat)]

    if not tick_positions:
        tick_positions = list(range(0, len(x_pairs), max(1, len(x_pairs) // 12)))

    return sorted(set(tick_positions))


def plot_density_contours(data: EarthgramData, longitudes: tuple[float, ...] = (0.0, 180.0)) -> None:
    import matplotlib
    import numpy as np

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    from matplotlib.ticker import LogFormatterSciNotation

    normalized_longitudes = tuple(_normalize_longitude(lon) for lon in longitudes)
    data = _coalesce_longitudes(data)

    x, y, mean_density, x_pairs, _ = _build_grids(data, normalized_longitudes, "mean density")
    _, _, std_density, _, _ = _build_grids(data, normalized_longitudes, "standard deviations density")
    x_labels = [_format_sweep_label(lat, lon) for lat, lon in x_pairs]

    if np.all(np.isnan(mean_density)):
        raise ValueError("No mean density data found for the selected longitudes.")

    positive_mean = mean_density[(~np.isnan(mean_density)) & (mean_density > 0.0)]
    if positive_mean.size == 0:
        raise ValueError("Mean density values are not positive; cannot use logarithmic color scale.")

    mean_min = positive_mean.min()
    mean_max = positive_mean.max()
    mean_levels = np.geomspace(mean_min, mean_max, 11)
    mean_ticks = np.geomspace(mean_min, mean_max, 10)
    std_valid = std_density[~np.isnan(std_density)]
    std_levels = np.linspace(std_valid.min(), std_valid.max(), 11) if std_valid.size else 11

    fig_mean, ax_mean = plt.subplots(1, 1, figsize=(9.75, 5), constrained_layout=True)

    c1 = ax_mean.contourf(x, y, mean_density, levels=mean_levels, norm=LogNorm(vmin=mean_min, vmax=mean_max), cmap="inferno")
    mean_contour_levels = np.geomspace(mean_min, mean_max, 6)
    mean_lines = ax_mean.contour(
        x,
        y,
        mean_density,
        levels=mean_contour_levels,
        colors="white",
        linewidths=1.0,
        alpha=1.0,
    )
    ax_mean.clabel(
    mean_lines,
    mean_contour_levels,
    inline=True,
    fontsize=10,
    fmt="%.1e",
    manual=[(10,120), (20,100), (30,90), (40,40)] # spaces out labels
    )
    ax_mean.set_title(f"Mean Density Along Latitude Sweep")
    ax_mean.set_xlabel("Latitude Sweep")
    ax_mean.set_ylabel(r"Altitude $(\mathrm{km})$")
    # --- colorbar with visible ticks ---
    cbar = fig_mean.colorbar(c1, ax=ax_mean)
    cbar.set_label(r"Mean Density $(\mathrm{kg}/\mathrm{m}^3)$")
    cbar.set_ticks(mean_ticks)
    cbar.ax.set_yticklabels([f"{t:.1e}" for t in mean_ticks])


    fig_std, ax_std = plt.subplots(1, 1, figsize=(9.75, 5), constrained_layout=True)
    c2 = ax_std.contourf(x, y, std_density, levels=std_levels, cmap="inferno")
    ax_std.set_title(r"Standard Deviation Density Along Latitude Sweep: $\sigma/\langle \rho \rangle$")
    ax_std.set_xlabel("Latitude Sweep")
    ax_std.set_ylabel(r"Altitude $(\mathrm{km})$")
    fig_std.colorbar(c2, ax=ax_std, label=r"Standard Deviation Density $(\%)$")

    tick_positions = _build_tick_positions(x_pairs, preferred_longitude=normalized_longitudes[0])
    for ax in (ax_mean, ax_std):
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([x_labels[idx] for idx in tick_positions], rotation=45, ha="right")
        ax.grid(True, which="major", axis="both", linestyle=":", color="white", linewidth=1.5, alpha=0.5)

    mean_output_path = Path("earthgram_mean_density.png")
    std_output_path = Path("earthgram_std_density.png")
    fig_mean.savefig(mean_output_path, dpi=200)
    fig_std.savefig(std_output_path, dpi=200)
    print(f"Saved contour figure: {mean_output_path}")
    print(f"Saved contour figure: {std_output_path}")


def main() -> None:
    longitude_order = (0.0, 180.0)

    # Input format: altitude (km) -> EarthGRAM file for that altitude.
    earthgram_files: dict[float, str] = {
         5.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_5km_LIST.md",
        15.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_15km_LIST.md",
        25.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_25km_LIST.md",
        35.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_35km_LIST.md",
        45.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_45km_LIST.md",
        55.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_55km_LIST.md",
        65.0: "/home/mitch/odrive-agent-mount/OneDrive For Business/CUBoulder/NGPDL/mitll_shs/cases/conditions/condition_sweep/lat_sweep_65km_LIST.md",
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
