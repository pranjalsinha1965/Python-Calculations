# from dataclasses import dataclass


# @dataclass
# class BeamCheckResult:
#     maximum_bending_moment_kn_m: float
#     rho: float
#     utilisation: float
#     bending_stress_mpa: float
#     midspan_deflection_mm: float
#     deflection_limit_mm: float
#     stress_result: str
#     deflection_result: str


# def beam_check(
#     span: float,
#     uniform_load: float,
#     section_modulus: float,
#     second_moment_of_area: float,
#     youngs_modulus: float,
#     yield_strength: float,
#     deflection_limit_ratio: float,
#     input_units: str = "si",
# ) -> BeamCheckResult:
#     """
#     Perform a simply supported beam check.

#     Parameters
#     ----------
#     span : float
#         Beam span. SI input: m. Imperial input: ft.
#     uniform_load : float
#         Uniformly distributed load. SI input: kN/m.
#         Imperial input: kip/ft.
#     section_modulus : float
#         Section modulus. SI input: cm^3. Imperial input: in^3.
#     second_moment_of_area : float
#         Second moment of area. SI input: cm^4. Imperial input: in^4.
#     youngs_modulus : float
#         Young's modulus. SI input: GPa. Imperial input: ksi.
#     yield_strength : float
#         Yield strength. SI input: MPa. Imperial input: ksi.
#     deflection_limit_ratio : float
#         Deflection denominator n for limit L/n.
#     input_units : str
#         "si" or "imperial".
#     """

#     values = [
#         span,
#         uniform_load,
#         section_modulus,
#         second_moment_of_area,
#         youngs_modulus,
#         yield_strength,
#         deflection_limit_ratio,
#     ]

#     if any(value <= 0 for value in values):
#         raise ValueError("All engineering inputs must be greater than zero.")

#     if input_units not in {"si", "imperial"}:
#         raise ValueError("input_units must be 'si' or 'imperial'.")

#     # -----------------------------------------------------------------
#     # IMPORTANT:
#     # Keep your already verified workbook-equivalent formulas here.
#     # Do not duplicate those formulas in Streamlit or Lambda.
#     # -----------------------------------------------------------------

#     if input_units == "imperial":
#         span = span * 0.3048
#         uniform_load = uniform_load * 14.59390294
#         section_modulus = section_modulus * 1.6387064e-5
#         second_moment_of_area = second_moment_of_area * 4.162314256e-7
#         youngs_modulus = youngs_modulus * 6.894757293
#         yield_strength = yield_strength * 6.894757293

#     # Replace these calculation expressions with the final,
#     # workbook-verified formulas from your project.
#     maximum_bending_moment_kn_m = uniform_load * span**2 / 8

#     bending_stress_mpa = (
#         maximum_bending_moment_kn_m * 1000
#     ) / section_modulus

#     rho = bending_stress_mpa / yield_strength
#     utilisation = rho

#     stress_result = "PASS" if utilisation <= 1.0 else "FAIL"

#     # Example deflection calculation must match your verified workbook.
#     # Convert E from GPa to kN/m² and I from m^4.
#     e_kn_per_m2 = youngs_modulus * 1_000_000
#     deflection_m = (
#         5 * uniform_load * span**4
#     ) / (384 * e_kn_per_m2 * second_moment_of_area)

#     midspan_deflection_mm = deflection_m * 1000
#     deflection_limit_mm = (span * 1000) / deflection_limit_ratio

#     deflection_result = (
#         "PASS"
#         if midspan_deflection_mm <= deflection_limit_mm
#         else "FAIL"
#     )

#     return BeamCheckResult(
#         maximum_bending_moment_kn_m=maximum_bending_moment_kn_m,
#         rho=rho,
#         utilisation=utilisation,
#         bending_stress_mpa=bending_stress_mpa,
#         midspan_deflection_mm=midspan_deflection_mm,
#         deflection_limit_mm=deflection_limit_mm,
#         stress_result=stress_result,
#         deflection_result=deflection_result,
#     )

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
