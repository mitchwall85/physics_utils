"""Example script: read all EarthGRAM outputs in a directory and plot envelopes."""

from __future__ import annotations

from pathlib import Path

try:
    from .plot_earthgram_envelope import plot_envelopes
except ImportError:
    from plot_earthgram_envelope import plot_envelopes


def main() -> None:
    input_dir = Path("/path/to/earthgram_outputs")
    file_pattern = "*.md"

    density_path, perturbation_path = plot_envelopes(
        input_dir=input_dir,
        pattern=file_pattern,
        output_prefix="earthgram",
    )

    print(f"Saved envelope figure: {density_path}")
    print(f"Saved perturbation figure: {perturbation_path}")


if __name__ == "__main__":
    main()
