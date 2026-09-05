# Verification & Validation — Beam Check

## Scope and distinction

I treated **validation** as checking that the mathematical model is appropriate for the intended physical problem, and **verification** as checking that the Python implementation correctly solves that model. This follows the NAFEMS distinction between validation and verification.

## Validation — are these the right equations?

The workbook is a simply supported beam with a full-span uniformly distributed load. I checked its formulas against standard closed-form beam equations:

- `M_max = w L² / 8`
- `σ = M_max / S`
- `utilisation = σ / fy`
- `δ_max = 5 w L⁴ / (384 E I)`
- `δ_limit = L / n`

The formulas for a simply supported beam under UDL are independently stated at https://calcs.com/freetools/beam-analysis. The workbook therefore uses the expected elastic beam equations for this idealised load/support case.

Assumptions: simply supported beam, full-span UDL, constant `E` and `I`, linear-elastic small-deflection beam theory, and the supplied section properties are applicable. This task does **not** establish validation against physical test data; it validates the identified mathematical model against the stated engineering formulation.

## Verification — does the Python solve them correctly?

For the workbook's pre-filled inputs `(L=6 m, w=10 kN/m, S=597 cm³, I=8503 cm⁴, E=200 GPa, fy=275 MPa, n=360)`, the Python outputs are:
:--------------------------------------------------------------------------:
| Output           | Workbook calculation | Python         | Tolerance     |
|------------------|---------------------:|---------------:|--------------:|
| M                | 45.000000 kN·m       | 45.000000 kN·m | 1e-12 rel/abs |
| σ                | 75.376884 MPa        | 75.376884 MPa  | 1e-10 rel     |
| utilisation      | 0.274097762          | 0.274097762    | 1e-10 rel     |
| δ                | 9.922968 mm          | 9.922968 mm    | 1e-10 rel     |
| limit            | 16.666667 mm         | 16.666667 mm   | 1e-10 rel     |
| stress check     | PASS                 | PASS           | exact         |
| deflection check | PASS                 | PASS           | exact         |
:--------------------------------------------------------------------------:

The tolerances are tight because these are deterministic closed-form calculations with no iterative solver or measured-data uncertainty. The tests use `pytest.approx` explicitly.

### Undocumented workbook constant

The workbook contains `Calculation!E2 = 100000`, which is used only in the deflection formula. It is a **composite unit-conversion factor**, not an additional engineering coefficient. With the workbook's numerical units (`w` in kN/m, `L` in m, `E` in GPa, `I` in cm⁴), the raw expression has to be multiplied by `100000` to report deflection in mm. This is equivalent to converting kN→N, GPa→Pa, cm⁴→m⁴ and m→mm in one combined factor. I did not copy this unexplained constant into the Python calculation; instead, Python converts inputs to SI at the boundary and therefore needs no equivalent hard-coded `100000`.

### Important correction from the AI-assisted work

An earlier AI-assisted version was not sufficiently verified: its test import path did not match the three-file submission layout, so the submitted test suite did not run in that form. I corrected the test to import `beam_check` from the same directory. I also independently recomputed the deflection using SI units and checked it against the workbook formula, rather than assuming the earlier implementation was correct.

The final three files were then checked together with `pytest`; the final suite contains 20 tests and the expected result is **20 passed**.

If a future comparison does not reproduce, I would stop and report the discrepancy rather than alter the Python or test expected values merely to force agreement.

## Units and conversion references

Imperial inputs are converted at the input boundary using NIST SP 811 Appendix B conversion factors: https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8

The implemented factors include `1 ft = 0.3048 m`, `1 in = 0.0254 m`, `1 kip = 4448.2216152605 N`, `1 in³ = (0.0254 m)³`, `1 in⁴ = (0.0254 m)⁴`, and `1 ksi = 6.894757×10⁶ Pa`.

## AI policy

AI assistance was used to help inspect the spreadsheet formulas, draft the Python structure/tests, and draft this V&V note. I treated AI output as unverified. The most significant correction was the import/reproducibility issue and the need to independently check the deflection conversion. I checked the formulas directly against the workbook, recalculated the numerical outputs independently, and ran the final pytest suite.

**AI tool used: OpenAI ChatGPT.** I used it as an engineering/software-assistance tool, not as the authority for the calculation.

Examples of how I used it:

* **Formula identification:** ChatGPT helped translate the spreadsheet formulas into explicit equations. For example, `Calculation!B2 = wL²/8` was identified as the maximum bending moment for a simply supported beam under a full-span UDL, and `B6` as the standard `5wL⁴/(384EI)` deflection equation.
* **Code drafting:** ChatGPT helped draft the Python function, SI boundary conversions, dataclass output structure, and pytest cases.
* **V&V drafting:** ChatGPT helped structure this note around the distinction between validation (are the equations/model appropriate?) and verification (does the Python implement them correctly?).

### Most significant AI output checked/corrected

The most important issue was **not accepting an AI-generated result simply because it looked plausible**. An earlier version of the code/test submission had a reproducibility problem: the test import did not reliably match the three-file submission layout. I corrected the import to `from beam_check import ...` and then ran the test suite from a directory containing only the three submission files.

I also independently checked the deflection conversion. For the workbook inputs:

`L = 6 m`, `w = 10 kN/m`, `E = 200 GPa`, `I = 8503 cm⁴`

the SI calculation gives:

`δ = 5(10,000)(6⁴) / [384(200×10⁹)(8503×10⁻⁸)] = 0.009922968364 m`

which is **9.922968364 mm**. This was checked against the spreadsheet's use of `Calculation!E2 = 100000`, rather than copying the spreadsheet constant blindly into Python.

Finally, I ran the submitted tests with:

`python -m pytest -q`

and obtained **20 passed**. The test suite therefore verifies both the numerical workbook case and additional boundary/error cases. I would not change an expected value solely to make a test pass; if a discrepancy cannot be explained from the workbook, equations, units, or implementation, I would report it explicitly.

