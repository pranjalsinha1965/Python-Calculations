from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

InputUnitSystem = Literal["si", "imperial"]

@dataclass(frozen=True)
class BeamCheckResult:
    """Outputs reported in the same units as the workbook."""
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
IN3_TO_M3 = IN_TO_M**3
IN4_TO_M4 = IN_TO_M**4
KSI_TO_PA = KIP_TO_N / IN_TO_M**2

def _require_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero; got {value!r}")

def beam_check(span: float, uniform_load: float, section_modulus: float,
               second_moment_of_area: float, youngs_modulus: float,
               yield_strength: float, deflection_limit_ratio: float,
               *, input_units: InputUnitSystem = "si") -> BeamCheckResult:
    """Check a simply supported beam under a full-span uniform load.

    SI: m, kN/m, cm^3, cm^4, GPa, MPa.
    Imperial: ft, kip/ft, in^3, in^4, ksi, ksi.
    All calculations are performed in SI base units.

    M_max = w*L^2/8
    sigma = M_max/S
    utilisation = sigma/fy
    delta_max = 5*w*L^4/(384*E*I)
    delta_limit = L/n
    """
    for name, value in (("span", span), ("uniform_load", uniform_load),
                        ("section_modulus", section_modulus),
                        ("second_moment_of_area", second_moment_of_area),
                        ("youngs_modulus", youngs_modulus),
                        ("yield_strength", yield_strength),
                        ("deflection_limit_ratio", deflection_limit_ratio)):
        _require_positive(name, value)

    if input_units == "si":
        span_m = span
        uniform_load_n_per_m = uniform_load * 1000.0
        section_modulus_m3 = section_modulus * 1e-6
        second_moment_of_area_m4 = second_moment_of_area * 1e-8
        youngs_modulus_pa = youngs_modulus * 1e9
        yield_strength_pa = yield_strength * 1e6
    elif input_units == "imperial":
        span_m = span * FT_TO_M
        uniform_load_n_per_m = uniform_load * KIP_TO_N / FT_TO_M
        section_modulus_m3 = section_modulus * IN3_TO_M3
        second_moment_of_area_m4 = second_moment_of_area * IN4_TO_M4
        youngs_modulus_pa = youngs_modulus * KSI_TO_PA
        yield_strength_pa = yield_strength * KSI_TO_PA
    else:
        raise ValueError("input_units must be 'si' or 'imperial'")

    maximum_bending_moment_n_m = uniform_load_n_per_m * span_m**2 / 8.0
    bending_stress_pa = maximum_bending_moment_n_m / section_modulus_m3
    utilisation = bending_stress_pa / yield_strength_pa
    midspan_deflection_m = (5.0 * uniform_load_n_per_m * span_m**4 /
                            (384.0 * youngs_modulus_pa * second_moment_of_area_m4))
    deflection_limit_m = span_m / deflection_limit_ratio

    return BeamCheckResult(
        maximum_bending_moment_kn_m=maximum_bending_moment_n_m / 1000.0,
        bending_stress_mpa=bending_stress_pa / 1e6,
        utilisation=utilisation,
        midspan_deflection_mm=midspan_deflection_m * 1000.0,
        deflection_limit_mm=deflection_limit_m * 1000.0,
        stress_result="PASS" if utilisation <= 1.0 else "FAIL",
        deflection_result="PASS" if midspan_deflection_m <= deflection_limit_m else "FAIL",
    )