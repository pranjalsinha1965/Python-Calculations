import os

from dataclasses import dataclass

from typing import Literal

import requests
import streamlit as st


st.set_page_config(
    page_title="Steel Beam Calculator",
    page_icon="🏗️",
    layout="centered",
)


API_URL = os.getenv(
    "BEAM_API_URL",
    "https://c13k4t0su3.execute-api.ap-south-1.amazonaws.com/calculate",
)


st.title("🏗️ Steel Beam Calculator")

st.write(
    "Simply supported beam subjected to a uniformly distributed load."
)


unit_system = st.selectbox(
    "Input Unit System",
    ["si", "imperial"],
)


if unit_system == "si":

    span_label = "Span, L (m)"
    load_label = "Uniform Load, w (kN/m)"
    section_modulus_label = "Section Modulus, S (cm³)"
    inertia_label = "Second Moment of Area, I (cm⁴)"
    modulus_label = "Young's Modulus, E (GPa)"
    strength_label = "Yield Strength, fy (MPa)"

else:

    span_label = "Span, L (ft)"
    load_label = "Uniform Load, w (kip/ft)"
    section_modulus_label = "Section Modulus, S (in³)"
    inertia_label = "Second Moment of Area, I (in⁴)"
    modulus_label = "Young's Modulus, E (ksi)"
    strength_label = "Yield Strength, fy (ksi)"


col1, col2 = st.columns(2)

with col1:

    span = st.number_input(
        span_label,
        min_value=0.0001,
        value=6.0,
    )

    uniform_load = st.number_input(
        load_label,
        min_value=0.0001,
        value=10.0,
    )

    section_modulus = st.number_input(
        section_modulus_label,
        min_value=0.0001,
        value=597.0,
    )


with col2:

    second_moment_of_area = st.number_input(
        inertia_label,
        min_value=0.0001,
        value=8503.0,
    )

    youngs_modulus = st.number_input(
        modulus_label,
        min_value=0.0001,
        value=200.0,
    )

    yield_strength = st.number_input(
        strength_label,
        min_value=0.0001,
        value=275.0,
    )


deflection_limit_ratio = st.number_input(
    "Deflection Limit Ratio, n",
    min_value=1.0,
    value=360.0,
)


if st.button(
    "Calculate Beam",
    type="primary",
    use_container_width=True,
):

    payload = {
        "span": span,
        "uniform_load": uniform_load,
        "section_modulus": section_modulus,
        "second_moment_of_area": second_moment_of_area,
        "youngs_modulus": youngs_modulus,
        "yield_strength": yield_strength,
        "deflection_limit_ratio": deflection_limit_ratio,
        "input_units": unit_system,
    }

    try:

        with st.spinner("Calculating..."):

            response = requests.post(
                API_URL,
                json=payload,
                timeout=15,
            )

        data = response.json()

        if not response.ok:

            st.error(
                data.get(
                    "error",
                    "Calculation request failed.",
                )
            )

        elif data.get("success"):

            result = data["result"]

            st.success(
                f"Calculation completed: "
                f"{data['calculation_id']}"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Maximum Moment",
                (
                    f"{result['maximum_bending_moment_kn_m']:.3f} "
                    "kN·m"
                ),
            )

            col2.metric(
                "Bending Stress",
                (
                    f"{result['bending_stress_mpa']:.3f} "
                    "MPa"
                ),
            )

            col3.metric(
                "Utilisation",
                f"{result['utilisation']:.4f}",
            )

            col4, col5 = st.columns(2)

            col4.metric(
                "Deflection",
                (
                    f"{result['midspan_deflection_mm']:.3f} "
                    "mm"
                ),
            )

            col5.metric(
                "Deflection Limit",
                (
                    f"{result['deflection_limit_mm']:.3f} "
                    "mm"
                ),
            )

            stress_result = result["stress_result"]
            deflection_result = result["deflection_result"]

            if stress_result == "PASS":
                st.success(
                    f"Stress Check: {stress_result}"
                )
            else:
                st.error(
                    f"Stress Check: {stress_result}"
                )

            if deflection_result == "PASS":
                st.success(
                    f"Deflection Check: {deflection_result}"
                )
            else:
                st.error(
                    f"Deflection Check: {deflection_result}"
                )

        else:
            st.error(
                data.get(
                    "error",
                    "Unknown calculation error.",
                )
            )

    except requests.RequestException as error:
        st.error(
            f"Unable to contact calculation API: {error}"
        )

