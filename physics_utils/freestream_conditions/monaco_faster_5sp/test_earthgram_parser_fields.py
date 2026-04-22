from pathlib import Path

from physics_utils.freestream_conditions.monaco_faster_5sp.earthgram_parser import read_earthgram_output


def test_parses_speed_of_sound_and_specific_heat_ratio_from_realistic_record(tmp_path: Path) -> None:
    # Mirrors the EarthGRAM 4-column Field/Value table layout used in sweep_LIST.md outputs.
    content = """
--------------------
## Record #1
--------------------

| Field                             | Value      | Field                             | Value      |
|-----------------------------------|------------|-----------------------------------|------------|
| Elapsed Time (s)                  | 1.00       | Local Solar Time (hrs)            | 11.94      |
| Height Above Ref. Ellipsoid (km)  | 0.000      | Reference Radius (km)             | 6378.1     |
| Latitude (deg)                    | 0.000      | Geodetic Latitude (deg)           | 0.000      |
| Longitude E (deg)                 | 0.00       | Longitude of the Sun (deg)        | 280.53     |
| Subsolar Latitude (deg)           | -22.88     | Subsolar Longitude E (deg)        | 0.94       |
| Pressure Scale Height (km)        | 8.914      | Orbital Radius (AU)               | 0.98       |
| Density Scale Height (km)         | 10.966     | Solar Zenith Angle (deg)          | 23.04      |
| Sigma Level                       | 1.000      | Gravity (m/s^2)                   | 9.780      |
| Pressure Altitude (km)            | -0.000     | Speed of Sound (m/s)              | 344.526    |
| Compressibility Factor (zeta)     | 0.9995     | Perturbed Speed of Sound (m/s)    | 344.852    |
| Specific Heat Ratio               | 1.362      | Profile Weight                    | 0.000      |
| Specific Gas Constant (J/(kg K))  | 290.301    | RRA Site Name                     |            |
| Severity Level                    | 0          | RRA Weight                        | 0.000      |
""".strip()

    file_path = tmp_path / "sweep_LIST.md"
    file_path.write_text(content, encoding="utf-8")

    data = read_earthgram_output(file_path)

    # Location keys are parsed from Latitude / Longitude E / Height Above Ref. Ellipsoid.
    record = data[0.0][0.0][0.0]

    # Requested fields are parsed as normalized keys and numeric values.
    assert record["speed of sound"] == 344.526
    assert record["specific heat ratio"] == 1.362
