from dataclasses import dataclass


@dataclass
class BeamCheckResult:
    maximum_bending_moment_kn_m: float
    rho: float
    utilisation: float
    bending_stress_mpa: float
    midspan_deflection_mm: float
    deflection_limit_mm: float
    stress_result: str
    deflection_result: str


def beam_check(
    span: float,
    uniform_load: float,
    section_modulus: float,
    second_moment_of_area: float,
    youngs_modulus: float,
    yield_strength: float,
    deflection_limit_ratio: float,
    input_units: str = "si",
) -> BeamCheckResult:
    """
    Perform a simply supported beam check.

    Parameters
    ----------
    span : float
        Beam span. SI input: m. Imperial input: ft.
    uniform_load : float
        Uniformly distributed load. SI input: kN/m.
        Imperial input: kip/ft.
    section_modulus : float
        Section modulus. SI input: cm^3. Imperial input: in^3.
    second_moment_of_area : float
        Second moment of area. SI input: cm^4. Imperial input: in^4.
    youngs_modulus : float
        Young's modulus. SI input: GPa. Imperial input: ksi.
    yield_strength : float
        Yield strength. SI input: MPa. Imperial input: ksi.
    deflection_limit_ratio : float
        Deflection denominator n for limit L/n.
    input_units : str
        "si" or "imperial".
    """

    values = [
        span,
        uniform_load,
        section_modulus,
        second_moment_of_area,
        youngs_modulus,
        yield_strength,
        deflection_limit_ratio,
    ]

    if any(value <= 0 for value in values):
        raise ValueError("All engineering inputs must be greater than zero.")

    if input_units not in {"si", "imperial"}:
        raise ValueError("input_units must be 'si' or 'imperial'.")

    # -----------------------------------------------------------------
    # IMPORTANT:
    # Keep your already verified workbook-equivalent formulas here.
    # Do not duplicate those formulas in Streamlit or Lambda.
    # -----------------------------------------------------------------

    if input_units == "imperial":
        span = span * 0.3048
        uniform_load = uniform_load * 14.59390294
        section_modulus = section_modulus * 1.6387064e-5
        second_moment_of_area = second_moment_of_area * 4.162314256e-7
        youngs_modulus = youngs_modulus * 6.894757293
        yield_strength = yield_strength * 6.894757293

    # Replace these calculation expressions with the final,
    # workbook-verified formulas from your project.
    maximum_bending_moment_kn_m = uniform_load * span**2 / 8

    bending_stress_mpa = (
        maximum_bending_moment_kn_m * 1000
    ) / section_modulus

    rho = bending_stress_mpa / yield_strength
    utilisation = rho

    stress_result = "PASS" if utilisation <= 1.0 else "FAIL"

    # Example deflection calculation must match your verified workbook.
    # Convert E from GPa to kN/m² and I from m^4.
    e_kn_per_m2 = youngs_modulus * 1_000_000
    deflection_m = (
        5 * uniform_load * span**4
    ) / (384 * e_kn_per_m2 * second_moment_of_area)

    midspan_deflection_mm = deflection_m * 1000
    deflection_limit_mm = (span * 1000) / deflection_limit_ratio

    deflection_result = (
        "PASS"
        if midspan_deflection_mm <= deflection_limit_mm
        else "FAIL"
    )

    return BeamCheckResult(
        maximum_bending_moment_kn_m=maximum_bending_moment_kn_m,
        rho=rho,
        utilisation=utilisation,
        bending_stress_mpa=bending_stress_mpa,
        midspan_deflection_mm=midspan_deflection_mm,
        deflection_limit_mm=deflection_limit_mm,
        stress_result=stress_result,
        deflection_result=deflection_result,
    )