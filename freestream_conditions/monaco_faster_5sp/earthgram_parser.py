"""Utilities for parsing EarthGRAM text outputs into queryable dictionaries."""

from __future__ import annotations

import pickle
import re
from pathlib import Path
from typing import Any


RECORD_SPLIT_PATTERN = re.compile(r"^\s*##\s*Record\s*#\d+", re.IGNORECASE | re.MULTILINE)
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

        # Key-value pairs in a 4-column table: Field | Value | Field | Value
        if len(header) >= 4 and header[0].lower() == "field" and header[2].lower() == "field":
            for row in rows:
                if len(row) >= 2:
                    parsed[_normalize_label(row[0])] = _coerce_value(row[1])
                if len(row) >= 4:
                    parsed[_normalize_label(row[2])] = _coerce_value(row[3])
            continue

        # General table style: first column is row label, other columns are named metrics.
        row_header = _normalize_label(header[0])
        col_headers = [_normalize_label(h) for h in header[1:]]

        for row in rows:
            if len(row) < 2:
                continue

            row_name = _normalize_label(row[0])
            values = row[1:]
            for idx, value in enumerate(values):
                if idx >= len(col_headers):
                    continue
                col_name = col_headers[idx]
                if row_header == "field":
                    key = f"{row_name} {col_name}".strip()
                else:
                    key = f"{row_name} {col_name}".strip()
                parsed[key] = _coerce_value(value)

    return parsed


def read_earthgram_output(
    file_path: str | Path,
    pickle_name: str = "earthgram_records.pkl",
) -> dict[float, dict[float, dict[float, dict[str, Any]]]]:
    """Read an EarthGRAM output file and return/save a nested query dictionary.

    Returned dictionary shape:
    data[latitude][longitude][altitude][field_key] -> value
    """
    file_path = Path(file_path)
    text = file_path.read_text(encoding="utf-8")

    # Ignore preamble and keep record sections only.
    raw_records = RECORD_SPLIT_PATTERN.split(text)
    records = [record for record in raw_records if "|" in record]

    data: dict[float, dict[float, dict[float, dict[str, Any]]]] = {}

    for record in records:
        parsed = _parse_record(record)

        latitude = parsed.get("latitude")
        longitude = parsed.get("longitude e")
        altitude = parsed.get("height above ref. ellipsoid")

        if latitude is None or longitude is None or altitude is None:
            continue

        lat_key = float(latitude)
        lon_key = float(longitude)
        alt_key = float(altitude)

        data.setdefault(lat_key, {}).setdefault(lon_key, {})[alt_key] = parsed

    pickle_path = file_path.parent / pickle_name
    with pickle_path.open("wb") as handle:
        pickle.dump(data, handle)

    return data
