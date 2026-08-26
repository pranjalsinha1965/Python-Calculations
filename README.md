# Python-Calculations
Production-grade Python project converting an Excel steel-beam calculation into verified code. Calculates bending, stress, utilisation, deflection and PASS/FAIL results, supports SI/Imperial inputs, validates errors, uses pytest approximations, and compares outputs against the source workbook.

# Python Engineering Calculations — Simply Supported Beam Check

## Overview

This project converts an Excel engineering calculation into a verified Python implementation.

The source workbook, `source_workbook.xlsx`, checks a simply supported steel beam subjected to a uniformly distributed load. The objective is to reproduce the workbook calculation in Python, verify that the implementation produces the expected results, and validate the engineering equations against appropriate references.

The task is designed as a focused engineering software exercise with an expected working time of approximately 2–4 hours.

---

## Project Files(Important Modules)

```text
.
├── beam_check.py
├── test_beam_check.py
├── VV.md
├── README.md
└── source_workbook.xlsx
```

### `beam_check.py`

Contains the Python implementation of the beam calculation.

The module accepts the workbook inputs and returns the corresponding calculation outputs, including:

- Maximum bending moment, `M`
- Bending stress, `sigma`
- Stress utilisation
- Midspan deflection, `delta`
- Deflection limit
- Stress PASS/FAIL result
- Deflection PASS/FAIL result

The implementation is designed with explicit names, symbols, units, calculation steps, and outputs so that a deterministic downstream parser can infer the calculation structure for UI generation.

### `test_beam_check.py`

Contains automated tests using `pytest`.

The tests use explicit numerical tolerances with `pytest.approx` and include selected calculation points, workbook regression checks, unit-system checks, boundary checks, and invalid-input checks.

### `VV.md`

Contains the Verification and Validation note.

Verification and validation are treated separately in the NAFEMS sense:

- **Validation:** Are the selected engineering equations appropriate for the physical problem?
- **Verification:** Does the Python implementation solve those equations correctly?

This file also documents:

- Engineering references used
- Workbook-to-Python output comparison
- Numerical tolerances
- Assumptions
- Any discrepancies identified
- AI tools used and how their output was independently checked

---

## Engineering Problem

The calculation considers a simply supported steel beam subjected to a uniformly distributed load.

The source workbook uses the following inputs:

| Symbol | Description                | Workbook Unit |
|--------|----------------------------|---------------|
| `L`    | Beam span                  | m             |
| `w`    | Uniformly distributed load | kN/m          |
| `S`    | Section modulus            | cm³           |
| `I`    | Second moment of area      | cm⁴           |
| `E`    | Young's modulus            | GPa           |
| `fy`   | Yield strength             | MPa           |
| `n`    | Deflection limit ratio     | dimensionless |

For the pre-filled workbook case:

```text
L  = 6 m
w  = 10 kN/m
S  = 597 cm³
I  = 8503 cm⁴
E  = 200 GPa
fy = 275 MPa
n  = 360
```

---

## Governing Calculations

### 1. Maximum bending moment

For a simply supported beam carrying a uniformly distributed load:

```text
M = wL² / 8
```

---

### 2. Bending stress

The bending stress is calculated from:

```text
sigma = M / S
```

The Python implementation performs explicit unit conversion before calculation rather than relying on unexplained conversion multipliers.

---

### 3. Stress utilisation

```text
utilisation = sigma / fy
```

The stress check is:

```text
PASS if utilisation <= 1
FAIL otherwise
```

---

### 4. Maximum midspan deflection

For the loading and support condition represented by the workbook:

```text
delta = 5wL⁴ / (384EI)
```

The Python implementation performs this calculation using consistent SI units internally.

---

### 5. Deflection limit

The workbook defines the allowable deflection as:

```text
deflection_limit = L / n
```

where `n` is the configurable deflection limit ratio.

The deflection check is:

```text
PASS if delta <= deflection_limit
FAIL otherwise
```

---

## Unit Handling

### SI Calculation

All calculations are performed internally using SI units.

Examples of internal quantities include:

```text
Span                    m
Uniform load            N/m
Section modulus         m³
Second moment of area   m⁴
Young's modulus         Pa
Yield strength          Pa
Bending moment          N·m
Stress                  Pa
Deflection              m
```

Results are converted to suitable reporting units after calculation.

---

## Imperial Input Support

The calculation also supports Imperial inputs.

The Imperial input boundary accepts:

| Quantity              | Imperial Unit |
|-----------------------|---------------|
| Span                  | ft            |
| Uniform load          | kip/ft        |
| Section modulus       | in³           |
| Second moment of area | in⁴           |
| Young's modulus       | ksi           |
| Yield strength        | ksi           |

Imperial quantities are converted at the input boundary into SI units.

The calculation itself is then performed using SI units only.

The conversion factors and their sources are documented in `VV.md`.

---

## Input Validation

Invalid physical inputs are rejected.

A `ValueError` is raised for zero or negative values where the task requires positive quantities, including:

- Span
- Load
- Section modulus
- Second moment of area

Additional validation may also be applied where required to prevent physically invalid calculations.

---

## Undocumented Workbook Constant

The source workbook contains an undocumented hard-coded constant in the deflection calculation.

The workbook formula is equivalent to:

```text
5 × w × L⁴
---------------- × 100000
384 × E × I
```

The value:

```text
100000
```

is stored in an unlabeled workbook cell and acts as a unit-conversion multiplier because the spreadsheet mixes units such as:

```text
w → kN/m
L → m
E → GPa
I → cm⁴
delta → mm
```

This constant is specifically investigated and documented as part of the task.

The Python implementation does not rely on an unexplained `100000` multiplier. Instead, all quantities are explicitly converted to SI units before applying the governing deflection equation.

---

## Testing

Tests are implemented with `pytest`.

Numerical comparisons use explicit tolerances:

```python
pytest.approx(...)
```

The test suite includes:

1. **Workbook regression test**  
   Verifies the Python outputs against the workbook's pre-filled example.

2. **Imperial/SI equivalence test**  
   Verifies that physically equivalent inputs in both unit systems produce equivalent results.

3. **Stress boundary test**  
   Tests the PASS/FAIL behaviour at or near a utilisation of `1.0`.

4. **Deflection boundary test**  
   Tests the PASS/FAIL behaviour at or near the allowable deflection.

5. **Invalid input tests**  
   Confirms that invalid zero and negative inputs raise `ValueError`.

---

## Running the Calculation

Run the Python module according to the public API defined in `beam_check.py`.

Example usage:

```python
from beam_check import beam_check

result = beam_check(
    span_m=6.0,
    uniform_load_kn_per_m=10.0,
    section_modulus_cm3=597.0,
    second_moment_cm4=8503.0,
    youngs_modulus_gpa=200.0,
    yield_strength_mpa=275.0,
    deflection_limit_ratio=360.0,
)
```

The exact function signature and result structure are defined in `beam_check.py`.

---

## Running the Tests

Install the required testing dependency:

```bash
pip install pytest
```

Run:

```bash
pytest -v
```

---

## Verification and Validation

The `VV.md` document distinguishes between validation and verification.

### Validation — Are these the right equations?

This addresses:

- Whether the governing equations correspond to the beam and loading condition represented by the workbook
- Engineering references checked against the formulas
- Assumptions under which the formulas apply

### Verification — Does the code solve the equations correctly?

This addresses:

- Comparison between Python and workbook outputs
- Explicit numerical tolerances
- Reasons for the selected tolerances
- Boundary and invalid-input testing
- Any discrepancies found during implementation

If an output does not match the workbook and the discrepancy cannot be resolved, it is documented explicitly rather than artificially changing the implementation merely to force a match.

---

## AI Use

AI tools may be used during development for activities such as:

- Identifying candidate engineering formulas
- Assisting with Python implementation
- Suggesting test cases
- Drafting documentation

However, AI-generated results are independently checked against the source workbook, engineering references, unit consistency, and numerical calculations.

The specific tools used and the most significant item that required checking, correction, or rejection are documented in `VV.md`.

---

## Submission

The core submission consists of:

```text
beam_check.py
test_beam_check.py
VV.md
```

`README.md` is included as supporting documentation describing the calculation, project structure, units, testing approach, and how to run the submission.

## Miniconda Environment and Jupyter Kernel Setup

If the existing Miniconda environment has corrupted package archives or dependency issues, clean the Conda cache first:

```text
conda clean --all -y

del C:\Users\KIIT\miniconda3\pkgs\jupyterlab_widgets-3.0.16-py312haa95532_1.conda

conda clean --index-cache -y

conda clean --packages -y

conda clean --tarballs -y

conda update -n base -c defaults conda -y

conda create -n beam-task python=3.12 numpy pandas matplotlib openpyxl pytest jupyter ipykernel -y

conda activate beam-task

