import streamlit_app as st

from beam_check import beam_check


st.set_page_config(
    page_title="Steel Beam Calculator",
    page_icon="🏗️",
    layout="centered",
)

st.title("🏗️ Simply Supported Steel Beam Calculator")

st.write(
    """
    Calculate maximum bending moment, bending stress, utilisation,
    midspan deflection, and PASS/FAIL results for a simply supported
    beam subjected to a uniformly distributed load.
    """
)

st.divider()

input_units = st.selectbox(
    "Input Unit System",
    options=["si", "imperial"],
    format_func=lambda x: "SI Units" if x == "si" else "Imperial Units",
)


if input_units == "si":

    st.subheader("Beam Inputs — SI")

    col1, col2 = st.columns(2)

    with col1:
        span = st.number_input(
            "Span, L (m)",
            min_value=0.0001,
            value=6.0,
            step=0.1,
        )

        uniform_load = st.number_input(
            "Uniform Load, w (kN/m)",
            min_value=0.0001,
            value=10.0,
            step=0.1,
        )

        section_modulus = st.number_input(
            "Section Modulus, S (cm³)",
            min_value=0.0001,
            value=597.0,
            step=1.0,
        )

    with col2:
        second_moment_of_area = st.number_input(
            "Second Moment of Area, I (cm⁴)",
            min_value=0.0001,
            value=8503.0,
            step=1.0,
        )

        youngs_modulus = st.number_input(
            "Young's Modulus, E (GPa)",
            min_value=0.0001,
            value=200.0,
            step=1.0,
        )

        yield_strength = st.number_input(
            "Yield Strength, fy (MPa)",
            min_value=0.0001,
            value=275.0,
            step=1.0,
        )


else:

    st.subheader("Beam Inputs — Imperial")

    col1, col2 = st.columns(2)

    with col1:
        span = st.number_input(
            "Span, L (ft)",
            min_value=0.0001,
            value=19.685,
            step=0.1,
        )

        uniform_load = st.number_input(
            "Uniform Load, w (kip/ft)",
            min_value=0.0001,
            value=0.685,
            step=0.01,
        )

        section_modulus = st.number_input(
            "Section Modulus, S (in³)",
            min_value=0.0001,
            value=36.43,
            step=0.1,
        )

    with col2:
        second_moment_of_area = st.number_input(
            "Second Moment of Area, I (in⁴)",
            min_value=0.0001,
            value=2043.0,
            step=1.0,
        )

        youngs_modulus = st.number_input(
            "Young's Modulus, E (ksi)",
            min_value=0.0001,
            value=29007.5,
            step=10.0,
        )

        yield_strength = st.number_input(
            "Yield Strength, fy (ksi)",
            min_value=0.0001,
            value=39.89,
            step=1.0,
        )


st.divider()

deflection_limit_ratio = st.number_input(
    "Deflection Limit Ratio, n",
    min_value=1.0,
    value=360.0,
    step=1.0,
    help="Allowable deflection is calculated as L / n.",
)


if st.button("Calculate Beam Check", type="primary", use_container_width=True):

    try:

        result = beam_check(
            span=span,
            uniform_load=uniform_load,
            section_modulus=section_modulus,
            second_moment_of_area=second_moment_of_area,
            youngs_modulus=youngs_modulus,
            yield_strength=yield_strength,
            deflection_limit_ratio=deflection_limit_ratio,
            input_units=input_units,
        )

        st.divider()

        st.subheader("Calculation Results")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Maximum Moment, M",
            f"{result.maximum_bending_moment_kn_m:.3f} kN·m",
        )

        col2.metric(
            "Bending Stress, σ",
            f"{result.bending_stress_mpa:.3f} MPa",
        )

        col3.metric(
            "Utilisation, ρ",
            f"{result.utilisation:.4f}",
        )

        col4, col5 = st.columns(2)

        col4.metric(
            "Midspan Deflection, δ",
            f"{result.midspan_deflection_mm:.3f} mm",
        )

        col5.metric(
            "Deflection Limit",
            f"{result.deflection_limit_mm:.3f} mm",
        )

        st.divider()

        stress_col, deflection_col = st.columns(2)

        with stress_col:

            st.subheader("Stress Check")

            if result.stress_result == "PASS":
                st.success("PASS")
            else:
                st.error("FAIL")

        with deflection_col:

            st.subheader("Deflection Check")

            if result.deflection_result == "PASS":
                st.success("PASS")
            else:
                st.error("FAIL")

        st.divider()

        st.subheader("Calculation Summary")

        st.code(
            f"""
Maximum Moment M       = {result.maximum_bending_moment_kn_m:.3f} kN·m
Bending Stress σ       = {result.bending_stress_mpa:.3f} MPa
Utilisation ρ          = {result.utilisation:.4f}
Midspan Deflection δ   = {result.midspan_deflection_mm:.3f} mm
Deflection Limit       = {result.deflection_limit_mm:.3f} mm
Stress Check           = {result.stress_result}
Deflection Check       = {result.deflection_result}
"""
        )

    except ValueError as error:

        st.error(f"Input validation error: {error}")

    except Exception as error:

        st.error(f"Calculation error: {error}")