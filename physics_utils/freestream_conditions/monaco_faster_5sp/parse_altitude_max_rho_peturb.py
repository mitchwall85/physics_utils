"""Dump EarthGRAM density-perturbation table lines at a requested altitude.

This helper scans EarthGRAM markdown outputs, finds records at the selected
altitude (default 97.5 km), and writes the full "Perturbation (%)" row from
the pressure/density/temperature table to a text file. Each output line is
prefixed with latitude/longitude for manual verification.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from physics_utils.freestream_conditions.monaco_faster_5sp.earthgram_parser import _parse_record

RECORD_HEADER_PATTERN = re.compile(r"^\s*##\s*Record\s*#\s*(\d+)", re.IGNORECASE | re.MULTILINE)
PERTURBATION_LINE_PATTERN = re.compile(r"^\|\s*Perturbation\s*\(%\)\s*\|.*$", re.IGNORECASE | re.MULTILINE)


def _iter_records(file_path: Path) -> list[tuple[int, str]]:
    text = file_path.read_text(encoding="utf-8")
    headers = list(RECORD_HEADER_PATTERN.finditer(text))
    records: list[tuple[int, str]] = []

    for idx, header_match in enumerate(headers):
        record_id = int(header_match.group(1))
        start = header_match.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        records.append((record_id, text[start:end]))

    return records


def dump_density_perturbation_lines(
    input_dir: Path,
    output_path: Path,
    altitude_km: float = 97.5,
    pattern: str = "*.md",
    tolerance_km: float = 1e-6,
) -> int:
    matches: list[str] = []

    files = sorted(path for path in input_dir.glob(pattern) if path.is_file())
    if not files:
        raise FileNotFoundError(f"No files found in {input_dir} matching '{pattern}'.")

    for file_path in files:
        for record_id, record_text in _iter_records(file_path):
            if "|" not in record_text:
                continue

            parsed = _parse_record(record_text)
            altitude = parsed.get("height above ref. ellipsoid")
            latitude = parsed.get("latitude")
            longitude = parsed.get("longitude e")

            if altitude is None or latitude is None or longitude is None:
                continue

            if abs(float(altitude) - float(altitude_km)) > tolerance_km:
                continue

            line_match = PERTURBATION_LINE_PATTERN.search(record_text)
            if not line_match:
                continue

            full_line = line_match.group(0).strip()
            matches.append(
                f"lat={float(latitude):.3f}, lon={float(longitude):.3f}, alt={float(altitude):.3f}, "
                f"file={file_path.name}, record={record_id} :: {full_line}"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(matches) + ("\n" if matches else ""), encoding="utf-8")
    return len(matches)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract full EarthGRAM 'Perturbation (%)' table lines for records at a specific altitude "
            "and write them to a text file with lat/lon prefixes."
        )
    )
    parser.add_argument("input_dir", type=Path, help="Directory containing EarthGRAM markdown files.")
    parser.add_argument("--altitude-km", type=float, default=97.5, help="Target altitude in km (default: 97.5).")
    parser.add_argument("--pattern", default="*.md", help="Glob pattern for EarthGRAM files (default: *.md).")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("density_perturbation_lines_97p5km.txt"),
        help="Output text file path (default: density_perturbation_lines_97p5km.txt).",
    )
    parser.add_argument(
        "--tolerance-km",
        type=float,
        default=1e-6,
        help="Altitude matching tolerance in km (default: 1e-6).",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    count = dump_density_perturbation_lines(
        input_dir=args.input_dir,
        output_path=args.output,
        altitude_km=args.altitude_km,
        pattern=args.pattern,
        tolerance_km=args.tolerance_km,
    )
    print(f"Wrote {count} lines to {args.output}")


if __name__ == "__main__":
    main()
