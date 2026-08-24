from beam_check import beam_check

result = beam_check(
    span=6.0,
    uniform_load=10.0,
    section_modulus=597.0,
    second_moment_of_area=8503.0,
    youngs_modulus=200.0,
    yield_strength=275.0,
    deflection_limit_ratio=360.0,
    input_units="si",
)

print(result)