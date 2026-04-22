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

try:
    from ...dsmc.hs import hs_mfp
except ImportError:
    try:
        from physics_utils.dsmc.hs import hs_mfp
    except ImportError:
        import sys

        repo_root = Path(__file__).resolve().parents[3]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from physics_utils.dsmc.hs import hs_mfp


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


def _altitude_knudsen_profile(
    data: EarthgramData,
    d_avg_m: float,
    characteristic_length_m: float,
    number_density_key: str = "number density",
) -> tuple[np.ndarray, np.ndarray]:
    """Return altitude grid [km] and Knudsen number profile [-]."""
    alt_to_n: dict[float, list[float]] = {}

    for lon_map in data.values():
        for alt_map in lon_map.values():
            for altitude_km, fields in alt_map.items():
                n_val = fields.get(number_density_key)
                if n_val is None:
                    continue
                alt_to_n.setdefault(float(altitude_km), []).append(float(n_val))

    if not alt_to_n:
        raise ValueError(
            f"No '{number_density_key}' entries were parsed from this EarthGRAM file. "
            "Set --number-density-key if your file uses a different label."
        )

    if d_avg_m <= 0.0:
        raise ValueError("d_avg_m must be positive.")
    if characteristic_length_m <= 0.0:
        raise ValueError("characteristic_length_m must be positive.")

    altitudes_km = np.array(sorted(alt_to_n.keys()), dtype=float)
    n_profile = np.array([np.mean(alt_to_n[alt]) for alt in altitudes_km], dtype=float)

    lambda_m = hs_mfp(n_profile, d_avg_m)
    kn_profile = lambda_m / characteristic_length_m
    return altitudes_km, kn_profile


def _build_secondary_yaxis(
    ax: object,
    altitudes_km: np.ndarray,
    kn_profile: np.ndarray,
) -> object:
    """Add right-side secondary y-axis mapping altitude [km] to Knudsen number [-]."""
    # Enforce strictly increasing Kn for invertible interpolation functions.
    kn_monotonic = np.maximum.accumulate(np.asarray(kn_profile, dtype=float))

    positive_mask = kn_monotonic > 0.0
    if not np.any(positive_mask):
        return None

    alt_ref = altitudes_km[positive_mask]
    kn_ref = kn_monotonic[positive_mask]

    # If repeated values remain, nudge slightly to keep interpolation invertible.
    eps = np.finfo(float).eps
    for idx in range(1, len(kn_ref)):
        if kn_ref[idx] <= kn_ref[idx - 1]:
            kn_ref[idx] = kn_ref[idx - 1] + eps

    log_kn = np.log10(kn_ref)

    def alt_to_kn(alt_km: np.ndarray | float) -> np.ndarray:
        alt = np.asarray(alt_km, dtype=float)
        logk = np.interp(alt, alt_ref, log_kn)
        return np.power(10.0, logk)

    def kn_to_alt(kn: np.ndarray | float) -> np.ndarray:
        kn_arr = np.asarray(kn, dtype=float)
        kn_clip = np.clip(kn_arr, kn_ref.min(), kn_ref.max())
        logk = np.log10(kn_clip)
        return np.interp(logk, log_kn, alt_ref)

    y2 = ax.secondary_yaxis("right", functions=(alt_to_kn, kn_to_alt))
    y2.set_ylabel("Knudsen Number (-)")
    y2.set_yscale("log")
    return y2


def plot_mach_isocontours(
    earthgram_file: str | Path,
    altitude_min_km: float = 0.0,
    altitude_max_km: float = 200.0,
    velocity_min_kms: float = 0.0,
    velocity_max_kms: float = 12.0,
    velocity_samples: int = 241,
    d_avg_m: float = 3.7e-10,
    characteristic_length_m: float = 1.0,
    number_density_key: str = "number density",
    output_path: str | Path = "mach_isocontours_altitude_velocity.png",
) -> Path:
    """Create altitude-vs-velocity plot with Mach-number contour lines and a Knudsen axis."""
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = read_earthgram_output(earthgram_file)
    altitudes_km, speed_of_sound_ms = _altitude_speed_of_sound_profile(data)
    alt_kn_km, kn_profile = _altitude_knudsen_profile(
        data=data,
        d_avg_m=d_avg_m,
        characteristic_length_m=characteristic_length_m,
        number_density_key=number_density_key,
    )

    alt_mask = (altitudes_km >= float(altitude_min_km)) & (altitudes_km <= float(altitude_max_km))
    if not np.any(alt_mask):
        raise ValueError(
            "No EarthGRAM altitude records are inside the requested bounds: "
            f"[{altitude_min_km}, {altitude_max_km}] km."
        )

    altitudes_km = altitudes_km[alt_mask]
    speed_of_sound_ms = speed_of_sound_ms[alt_mask]

    kn_interp = np.interp(altitudes_km, alt_kn_km, kn_profile)

    velocity_kms = np.linspace(float(velocity_min_kms), float(velocity_max_kms), int(velocity_samples))
    vel_grid_kms, alt_grid_km = np.meshgrid(velocity_kms, altitudes_km)
    speed_grid_ms = speed_of_sound_ms[:, None]
    mach_grid = np.divide(vel_grid_kms * 1000.0, speed_grid_ms, where=speed_grid_ms > 0)

    fig, ax = plt.subplots(1, 1, figsize=(10, 6), constrained_layout=True)

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

    _build_secondary_yaxis(ax=ax, altitudes_km=altitudes_km, kn_profile=kn_interp)

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
        "--d-avg-m",
        type=float,
        default=3.7e-10,
        help="Hard-sphere effective molecular diameter in meters.",
    )
    parser.add_argument(
        "--characteristic-length-m",
        type=float,
        default=1.0,
        help="Reference length in meters for Kn = lambda / L_ref.",
    )
    parser.add_argument(
        "--number-density-key",
        type=str,
        default="number density",
        help="Normalized EarthGRAM key used for number density.",
    )
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
        d_avg_m=args.d_avg_m,
        characteristic_length_m=args.characteristic_length_m,
        number_density_key=args.number_density_key,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
