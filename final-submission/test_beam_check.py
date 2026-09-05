import pytest
from beam_check import beam_check, FT_TO_M, IN3_TO_M3, IN4_TO_M4, KIP_TO_N, KSI_TO_PA

WORKBOOK_INPUTS = dict(span=6.0, uniform_load=10.0, section_modulus=597.0,
    second_moment_of_area=8503.0, youngs_modulus=200.0, yield_strength=275.0,
    deflection_limit_ratio=360.0, input_units="si")

def test_prefilled_workbook_case():
    result = beam_check(**WORKBOOK_INPUTS)
    assert result.maximum_bending_moment_kn_m == pytest.approx(45.0, rel=1e-12, abs=1e-12)
    assert result.bending_stress_mpa == pytest.approx(75.37688442211055, rel=1e-10, abs=1e-12)
    assert result.utilisation == pytest.approx(0.27409776153494747, rel=1e-10, abs=1e-12)
    assert result.midspan_deflection_mm == pytest.approx(9.922968364106787, rel=1e-10, abs=1e-12)
    assert result.deflection_limit_mm == pytest.approx(16.666666666666668, rel=1e-10, abs=1e-12)
    assert result.stress_result == "PASS"
    assert result.deflection_result == "PASS"

def test_imperial_inputs_are_equivalent_to_si():
    si = beam_check(**WORKBOOK_INPUTS)
    imperial = beam_check(span=6.0 / FT_TO_M, uniform_load=(10000.0 * FT_TO_M) / KIP_TO_N,
        section_modulus=(597.0e-6) / IN3_TO_M3, second_moment_of_area=(8503.0e-8) / IN4_TO_M4,
        youngs_modulus=(200.0e9) / KSI_TO_PA, yield_strength=(275.0e6) / KSI_TO_PA,
        deflection_limit_ratio=360.0, input_units="imperial")
    assert imperial.maximum_bending_moment_kn_m == pytest.approx(si.maximum_bending_moment_kn_m, rel=1e-12, abs=1e-12)
    assert imperial.bending_stress_mpa == pytest.approx(si.bending_stress_mpa, rel=1e-12, abs=1e-12)
    assert imperial.utilisation == pytest.approx(si.utilisation, rel=1e-12, abs=1e-12)
    assert imperial.midspan_deflection_mm == pytest.approx(si.midspan_deflection_mm, rel=1e-12, abs=1e-12)
    assert imperial.deflection_limit_mm == pytest.approx(si.deflection_limit_mm, rel=1e-12, abs=1e-12)

@pytest.mark.parametrize("field", ["span", "uniform_load", "section_modulus", "second_moment_of_area", "youngs_modulus", "yield_strength", "deflection_limit_ratio"])
@pytest.mark.parametrize("value", [0.0, -1.0])
def test_non_positive_inputs_raise_value_error(field, value):
    inputs = WORKBOOK_INPUTS.copy(); inputs[field] = value
    with pytest.raises(ValueError): beam_check(**inputs)

def test_invalid_unit_system_raises_value_error():
    inputs = WORKBOOK_INPUTS.copy(); inputs["input_units"] = "metric"
    with pytest.raises(ValueError): beam_check(**inputs)

def test_stress_near_boundary_is_pass():
    inputs = WORKBOOK_INPUTS.copy(); inputs["yield_strength"] = 75.37688442211055 * (1.0 + 1e-6)
    result = beam_check(**inputs)
    assert result.utilisation < 1.0
    assert result.utilisation == pytest.approx(0.999999000001, rel=1e-9, abs=1e-12)
    assert result.stress_result == "PASS"

def test_stress_above_boundary_is_fail():
    inputs = WORKBOOK_INPUTS.copy(); inputs["yield_strength"] = 75.0
    result = beam_check(**inputs)
    assert result.utilisation > 1.0
    assert result.stress_result == "FAIL"

def test_deflection_boundary_is_pass():
    inputs = WORKBOOK_INPUTS.copy(); inputs["deflection_limit_ratio"] = 6.0 / 0.009922968364106787
    result = beam_check(**inputs)
    assert result.midspan_deflection_mm == pytest.approx(result.deflection_limit_mm, rel=1e-12, abs=1e-12)
    assert result.deflection_result == "PASS"