from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

InputUnitSystem = Literal["si", "imperial"]

@dataclass(frozen=True)
class BeamCheckResult:
    """Beam-check outputs in workbook reporting units."""
    maximum_bending_moment_kn_m: float
    bending_stress_mpa: float
    utilisation: float
    midspan_deflection_mm: float
    deflection_limit_mm: float
    stress_result: str
    deflection_result: str

FT_TO_M = 0.3048
KIP_TO_N = 4448.2216152605
IN_TO_M = 0.0254
IN3_TO_M3 = IN_TO_M ** 3
IN4_TO_M4 = IN_TO_M ** 4
KSI_TO_PA = KIP_TO_N / IN_TO_M ** 2

def _require_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero; got {value!r}")

def beam_check(
    span: float,
    uniform_load: float,
    section_modulus: float,
    second_moment_of_area: float,
    youngs_modulus: float,
    yield_strength: float,
    deflection_limit_ratio: float,
    *,
    input_units: InputUnitSystem = "si",
) -> BeamCheckResult:
    """
    Check a simply supported beam under a uniformly distributed load.

    SI input mode uses: m, kN/m, cm^3, cm^4, GPa, MPa.
    Imperial input mode uses: ft, kip/ft, in^3, in^4, ksi, ksi.

    Internal calculation units are SI base units.

    Calculation steps:
        M_max = w * L^2 / 8
        sigma = M_max / S
        utilisation = sigma / fy
        delta_max = 5 * w * L^4 / (384 * E * I)
        delta_limit = L / n
    """
    for name, value in (
        ("span", span),
        ("uniform_load", uniform_load),
        ("section_modulus", section_modulus),
        ("second_moment_of_area", second_moment_of_area),
        ("youngs_modulus", youngs_modulus),
        ("yield_strength", yield_strength),
        ("deflection_limit_ratio", deflection_limit_ratio),
    ):
        _require_positive(name, value)

    if input_units == "si":
        L_m = span
        w_n_per_m = uniform_load * 1_000.0
        S_m3 = section_modulus * 1e-6
        I_m4 = second_moment_of_area * 1e-8
        E_pa = youngs_modulus * 1e9
        fy_pa = yield_strength * 1e6
    elif input_units == "imperial":
        L_m = span * FT_TO_M
        w_n_per_m = uniform_load * KIP_TO_N / FT_TO_M
        S_m3 = section_modulus * IN3_TO_M3
        I_m4 = second_moment_of_area * IN4_TO_M4
        E_pa = youngs_modulus * KSI_TO_PA
        fy_pa = yield_strength * KSI_TO_PA
    else:
        raise ValueError("input_units must be 'si' or 'imperial'")

    M_n_m = w_n_per_m * L_m**2 / 8.0
    sigma_pa = M_n_m / S_m3
    utilisation = sigma_pa / fy_pa
    delta_m = 5.0 * w_n_per_m * L_m**4 / (384.0 * E_pa * I_m4)
    limit_m = L_m / deflection_limit_ratio

    return BeamCheckResult(
        maximum_bending_moment_kn_m=M_n_m / 1_000.0,
        bending_stress_mpa=sigma_pa / 1e6,
        utilisation=utilisation,
        midspan_deflection_mm=delta_m * 1_000.0,
        deflection_limit_mm=limit_m * 1_000.0,
        stress_result="PASS" if utilisation <= 1.0 else "FAIL",
        deflection_result="PASS" if delta_m <= limit_m else "FAIL",
    )
