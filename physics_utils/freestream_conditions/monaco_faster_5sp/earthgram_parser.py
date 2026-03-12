"""Utilities for parsing EarthGRAM text outputs into queryable dictionaries."""

from __future__ import annotations

import pickle
import re
from pathlib import Path
from typing import Any


RECORD_SPLIT_PATTERN = re.compile(r"^\s*##\s*Record\s*#\d+", re.IGNORECASE | re.MULTILINE)
RECORD_HEADER_PATTERN = re.compile(r"^\s*##\s*Record\s*#\s*(\d+)", re.IGNORECASE | re.MULTILINE)
NUMERIC_PATTERN = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$")


def _normalize_label(label: str) -> str:
    """Normalize table labels so they can be queried with consistent keys."""
    cleaned = label.strip().lower()
    cleaned = re.sub(r"\(.*?\)", "", cleaned)
    cleaned = cleaned.replace("%", " percent")
    cleaned = cleaned.replace("#", " number")
    cleaned = cleaned.replace("/", " ")
    cleaned = cleaned.replace("-", " ")
    cleaned = re.sub(r"[^a-z0-9\.\s]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _coerce_value(value: str) -> Any:
    """Convert values to float when possible, otherwise return stripped strings."""
    stripped = value.strip()
    if stripped == "":
        return None

    compact = stripped.replace(",", "")
    if NUMERIC_PATTERN.match(compact):
        return float(compact)

    return stripped


def _extract_table_blocks(text: str) -> list[list[str]]:
    """Extract consecutive markdown table lines into standalone blocks."""
    lines = text.splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        if "|" in line:
            current.append(line)
            continue

        if current:
            blocks.append(current)
            current = []

    if current:
        blocks.append(current)

    return blocks


def _parse_table_line(line: str) -> list[str]:
    parts = [part.strip() for part in line.strip().strip("|").split("|")]
    return [part for part in parts if part != ""]


def _is_separator_row(cells: list[str]) -> bool:
    return all(re.match(r"^:?-{2,}:?$", cell.replace(" ", "")) for cell in cells)


def _parse_record(record_text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}

    for block in _extract_table_blocks(record_text):
        if len(block) < 2:
            continue

        header = _parse_table_line(block[0])
        if not header:
            continue

        rows = [_parse_table_line(row) for row in block[1:]]
        rows = [row for row in rows if row and not _is_separator_row(row)]

        if not rows:
            continue

        if len(header) >= 4 and header[0].lower() == "field" and header[2].lower() == "field":
            for row in rows:
                if len(row) >= 2:
                    parsed[_normalize_label(row[0])] = _coerce_value(row[1])
                if len(row) >= 4:
                    parsed[_normalize_label(row[2])] = _coerce_value(row[3])
            continue

        col_headers = [_normalize_label(h) for h in header[1:]]
        for row in rows:
            if len(row) < 2:
                continue

            row_name = _normalize_label(row[0])
            for idx, value in enumerate(row[1:]):
                if idx >= len(col_headers):
                    continue
                col_name = col_headers[idx]
                parsed[f"{row_name} {col_name}".strip()] = _coerce_value(value)

    return parsed


def _read_single_earthgram_file(file_path: str | Path) -> dict[float, dict[float, dict[float, dict[str, Any]]]]:
    file_path = Path(file_path)
    text = file_path.read_text(encoding="utf-8")
    headers = list(RECORD_HEADER_PATTERN.finditer(text))
    records: list[tuple[int, str]] = []
    for idx, header_match in enumerate(headers):
        record_id = int(header_match.group(1))
        start = header_match.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        record_text = text[start:end]
        if "|" not in record_text:
            continue
        records.append((record_id, record_text))

    if not records:
        raw_records = RECORD_SPLIT_PATTERN.split(text)
        records = [(idx + 1, record) for idx, record in enumerate(raw_records) if "|" in record]

    data: dict[float, dict[float, dict[float, dict[str, Any]]]] = {}
    for record_id, record_text in records:
        parsed = _parse_record(record_text)
        parsed["record number"] = float(record_id)
        latitude = parsed.get("latitude")
        longitude = parsed.get("longitude e")
        altitude = parsed.get("height above ref. ellipsoid")

        if latitude is None or longitude is None or altitude is None:
            continue

        lat_key = float(latitude)
        lon_key = float(longitude)
        alt_key = float(altitude)
        data.setdefault(lat_key, {}).setdefault(lon_key, {})[alt_key] = parsed

    return data


def _merge_parsed_data(
    base: dict[float, dict[float, dict[float, dict[str, Any]]]],
    new_data: dict[float, dict[float, dict[float, dict[str, Any]]]],
    altitude_override: float | None = None,
) -> None:
    for lat, lon_map in new_data.items():
        for lon, alt_map in lon_map.items():
            for alt, fields in alt_map.items():
                target_alt = float(altitude_override) if altitude_override is not None else alt
                base.setdefault(lat, {}).setdefault(lon, {})[target_alt] = fields


def infer_altitude_from_filename(file_path: str | Path) -> float | None:
    """Infer altitude (km) from a filename when present.

    Supported examples include names like:
    - ``lat_sweep_80km_LIST.md``
    - ``earthgram_altitude_95.5_km.txt``
    - ``run_120.md`` (falls back to the last numeric token)
    """
    name = Path(file_path).stem

    km_match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*(?:km|kilometer|kilometre)s?", name, re.IGNORECASE)
    if km_match:
        return float(km_match.group(1))

    numeric_tokens = re.findall(r"[+-]?\d+(?:\.\d+)?", name)
    if numeric_tokens:
        return float(numeric_tokens[-1])

    return None


def find_earthgram_files(input_dir: str | Path, pattern: str = "*.md") -> list[Path]:
    """Return sorted EarthGRAM output files in a directory."""
    directory = Path(input_dir)
    files = sorted(path for path in directory.glob(pattern) if path.is_file())
    if not files:
        raise FileNotFoundError(f"No EarthGRAM output files found in {directory} matching pattern '{pattern}'.")
    return files


def build_altitude_file_map(
    input_dir: str | Path,
    pattern: str = "*.md",
    prefer_filename_altitude: bool = True,
) -> dict[float, Path]:
    """Build altitude(km)->file mapping for a directory of EarthGRAM outputs."""
    files = find_earthgram_files(input_dir=input_dir, pattern=pattern)
    altitude_files: dict[float, Path] = {}

    for idx, file_path in enumerate(files):
        altitude = infer_altitude_from_filename(file_path) if prefer_filename_altitude else None
        if altitude is None:
            altitude = float(idx)

        while altitude in altitude_files:
            altitude += 1e-6

        altitude_files[float(altitude)] = file_path

    return altitude_files


def read_earthgram_directory(
    input_dir: str | Path,
    pattern: str = "*.md",
    pickle_name: str = "earthgram_records.pkl",
    prefer_filename_altitude: bool = False,
) -> dict[float, dict[float, dict[float, dict[str, Any]]]]:
    """Read all EarthGRAM outputs in ``input_dir`` and return merged records.

    By default, altitude values are read from each EarthGRAM record directly.
    Set ``prefer_filename_altitude=True`` only when each file is a single-altitude
    slice and altitude should be forced from the filename.
    """
    files = find_earthgram_files(input_dir=input_dir, pattern=pattern)
    pickle_path = Path(input_dir) / pickle_name

    if prefer_filename_altitude:
        altitude_files = build_altitude_file_map(
            input_dir=input_dir,
            pattern=pattern,
            prefer_filename_altitude=True,
        )
        return read_earthgram_output(altitude_files, pickle_name=str(pickle_path))

    return read_earthgram_output(files, pickle_name=str(pickle_path))


def read_earthgram_output(
    earthgram_files: str | Path | dict[float, str | Path] | list[str | Path] | tuple[str | Path, ...],
    pickle_name: str = "earthgram_records.pkl",
) -> dict[float, dict[float, dict[float, dict[str, Any]]]]:
    """Read one or many EarthGRAM outputs and save a nested query dictionary.

    Parameters
    ----------
    earthgram_files
        Either:
        - path to one EarthGRAM output file, or
        - mapping of altitude (km) -> EarthGRAM output file path.
          Use this mapping when each EarthGRAM file contains one altitude slice.
        - list/tuple of EarthGRAM file paths.
          Uses altitude from each parsed record in each file (no override).

    Returns
    -------
    dict
        data[latitude][longitude][altitude][field_key] -> value
    """
    data: dict[float, dict[float, dict[float, dict[str, Any]]]] = {}

    if isinstance(earthgram_files, dict):
        for altitude, file_path in earthgram_files.items():
            parsed = _read_single_earthgram_file(file_path)
            _merge_parsed_data(data, parsed, altitude_override=float(altitude))
        pickle_path = Path(pickle_name)
    elif isinstance(earthgram_files, (list, tuple)):
        for file_path in earthgram_files:
            parsed = _read_single_earthgram_file(file_path)
            _merge_parsed_data(data, parsed)
        pickle_path = Path(pickle_name)
    else:
        file_path = Path(earthgram_files)
        data = _read_single_earthgram_file(file_path)
        pickle_path = file_path.parent / pickle_name

    with pickle_path.open("wb") as handle:
        pickle.dump(data, handle)

    return data
