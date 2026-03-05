"""Example workflow: parse one or more EarthGRAM outputs, pickle, and make contour plots."""

from __future__ import annotations

from pathlib import Path
import pickle

try:
    from .earthgram_parser import read_earthgram_output
except ImportError:
    from earthgram_parser import read_earthgram_output


EarthgramData = dict[float, dict[float, dict[float, dict[str, float]]]]


def _merge_data(base: EarthgramData, new_data: EarthgramData, altitude_override: float | None = None) -> None:
    """Merge parsed EarthGRAM dictionaries into `base` in-place."""
    for lat, lon_map in new_data.items():
        for lon, alt_map in lon_map.items():
            for alt, fields in alt_map.items():
                target_alt = float(altitude_override) if altitude_override is not None else alt
                base.setdefault(lat, {}).setdefault(lon, {})[target_alt] = fields


def read_multiple_earthgram_outputs(
    earthgram_files_by_altitude: dict[float, str | Path],
    pickle_name: str = "earthgram_records.pkl",
) -> EarthgramData:
    """Read multiple EarthGRAM files and return a single merged nested dictionary.

    Parameters
    ----------
    earthgram_files_by_altitude
        Mapping of altitude (km) to EarthGRAM text file path.
        If a file contains multiple records, all matching lat/lon points are merged using
        the altitude key from this mapping.
    pickle_name
        Output pickle name written to the current working directory.
    """
    merged: EarthgramData = {}

    for altitude, earthgram_file in earthgram_files_by_altitude.items():
        parsed = read_earthgram_output(earthgram_file, pickle_name=f"{Path(earthgram_file).stem}.pkl")
        _merge_data(merged, parsed, altitude_override=altitude)

    with Path(pickle_name).open("wb") as handle:
        pickle.dump(merged, handle)

    return merged


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

    # Use a headless backend so this script works on servers/CLI environments.
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
    # User inputs (no command-line arguments)
    longitude = 0.0
    earthgram_files_by_altitude = {
        70.0: "conditions_gram_mass_70.txt",
        80.0: "conditions_gram_mass_80.txt",
        85.0: "conditions_gram_mass_85.txt",
        110.0: "conditions_gram_mass_110.txt",
    }

    data = read_multiple_earthgram_outputs(
        earthgram_files_by_altitude,
        pickle_name="earthgram_records.pkl",
    )

    if not any(longitude in lon_map for lon_map in data.values()):
        raise ValueError(f"Longitude {longitude} is not present in parsed data.")

    print(f"Parsed {len(data)} latitude entries.")
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
