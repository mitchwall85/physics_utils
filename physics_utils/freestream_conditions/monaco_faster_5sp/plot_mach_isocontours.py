"""Plot Mach-number isocontours over altitude and velocity from EarthGRAM output."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import numpy as np

try:
    from .earthgram_parser import read_earthgram_output
except ImportError:
    from earthgram_parser import read_earthgram_output


EarthgramData = dict[float, dict[float, dict[float, dict[str, float]]]]


def _altitude_speed_of_sound_profile(data: EarthgramData) -> tuple[np.ndarray, np.ndarray]:
    """Return altitude grid [km] and mean speed-of-sound profile [m/s]."""
    alt_to_speeds: dict[float, list[float]] = {}

    for lon_map in data.values():
        for alt_map in lon_map.values():
            for altitude_km, fields in alt_map.items():
                speed_of_sound = fields.get("speed of sound")
                if speed_of_sound is None:
                    continue
                alt_to_speeds.setdefault(float(altitude_km), []).append(float(speed_of_sound))

    if not alt_to_speeds:
        raise ValueError(
            "No 'speed of sound' entries were parsed from this EarthGRAM file. "
            "Confirm the input includes a 'Speed of Sound (m/s)' field."
        )

    altitudes_km = np.array(sorted(alt_to_speeds.keys()), dtype=float)
    speed_profile = np.array([np.mean(alt_to_speeds[alt]) for alt in altitudes_km], dtype=float)
    return altitudes_km, speed_profile


def plot_mach_isocontours(
    earthgram_file: str | Path,
    altitude_min_km: float = 0.0,
    altitude_max_km: float = 200.0,
    velocity_min_kms: float = 0.0,
    velocity_max_kms: float = 12.0,
    velocity_samples: int = 241,
    output_path: str | Path = "mach_isocontours_altitude_velocity.png",
) -> Path:
    """Create altitude-vs-velocity plot with Mach-number contour lines."""
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = read_earthgram_output(earthgram_file)
    altitudes_km, speed_of_sound_ms = _altitude_speed_of_sound_profile(data)

    alt_mask = (altitudes_km >= float(altitude_min_km)) & (altitudes_km <= float(altitude_max_km))
    if not np.any(alt_mask):
        raise ValueError(
            "No EarthGRAM altitude records are inside the requested bounds: "
            f"[{altitude_min_km}, {altitude_max_km}] km."
        )

    altitudes_km = altitudes_km[alt_mask]
    speed_of_sound_ms = speed_of_sound_ms[alt_mask]

    velocity_kms = np.linspace(float(velocity_min_kms), float(velocity_max_kms), int(velocity_samples))
    velocity_ms = velocity_kms * 1000.0

    _, speed_grid = np.meshgrid(velocity_ms, speed_of_sound_ms)
    vel_grid_kms, alt_grid_km = np.meshgrid(velocity_kms, altitudes_km)
    mach_grid = np.divide(vel_grid_kms * 1000.0, speed_grid, where=speed_grid > 0)

    fig, ax = plt.subplots(1, 1, figsize=(9.5, 5.75), constrained_layout=True)

    filled_levels = np.linspace(max(0.0, np.nanmin(mach_grid)), np.nanmax(mach_grid), 25)
    cf = ax.contourf(vel_grid_kms, alt_grid_km, mach_grid, levels=filled_levels, cmap="viridis")

    contour_levels = np.array([0.8, 1, 2, 3, 5, 8, 10, 12, 15, 20, 25, 30], dtype=float)
    contour_levels = contour_levels[
        (contour_levels >= np.nanmin(mach_grid)) & (contour_levels <= np.nanmax(mach_grid))
    ]
    if contour_levels.size:
        cs = ax.contour(
            vel_grid_kms,
            alt_grid_km,
            mach_grid,
            levels=contour_levels,
            colors="white",
            linewidths=1.0,
        )
        ax.clabel(cs, inline=True, fontsize=9, fmt="M=%.1f")

    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label("Mach Number")

    ax.set_title("Mach Number Isocontours: Altitude vs Velocity")
    ax.set_xlabel("Velocity (km/s)")
    ax.set_ylabel("Altitude (km)")
    ax.set_xlim(float(velocity_min_kms), float(velocity_max_kms))
    ax.set_ylim(float(altitude_min_km), float(altitude_max_km))
    ax.grid(True, linestyle=":", alpha=0.5)

    output_path = Path(output_path)
    fig.savefig(output_path, dpi=200)
    print(f"Saved figure: {output_path}")
    return output_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot altitude-vs-velocity Mach contours from an EarthGRAM markdown output.",
    )
    parser.add_argument(
        "earthgram_file",
        type=Path,
        nargs="?",
        default=Path("sweep_LIST.md"),
        help="EarthGRAM output file path (default: ./sweep_LIST.md)",
    )
    parser.add_argument("--altitude-min-km", type=float, default=0.0)
    parser.add_argument("--altitude-max-km", type=float, default=200.0)
    parser.add_argument("--velocity-min-kms", type=float, default=0.0)
    parser.add_argument("--velocity-max-kms", type=float, default=12.0)
    parser.add_argument("--velocity-samples", type=int, default=241)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("mach_isocontours_altitude_velocity.png"),
        help="Output figure filename.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    plot_mach_isocontours(
        earthgram_file=args.earthgram_file,
        altitude_min_km=args.altitude_min_km,
        altitude_max_km=args.altitude_max_km,
        velocity_min_kms=args.velocity_min_kms,
        velocity_max_kms=args.velocity_max_kms,
        velocity_samples=args.velocity_samples,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
