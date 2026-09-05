# Beam Check — Verified Engineering Calculation

A small Python implementation of a spreadsheet-based simply supported steel-beam check. The project reproduces the workbook calculation for a full-span uniformly distributed load (UDL), performs calculations internally in SI units, supports both SI and Imperial inputs, and verifies the implementation with `pytest`.

## 1. Project overview

The source workbook checks two governing criteria:

1. **Bending stress**
2. **Midspan deflection**

The Python implementation deliberately separates:

- **Validation** — whether the mathematical model and equations are appropriate for the stated beam/load case.
- **Verification** — whether the Python implementation correctly solves those equations and reproduces the workbook outputs.

The final submission consists of:

```text
beam_check.py
test_beam_check.py
VV.md
```

The final three-file submission was executed with:

```bash
python -m pytest -q
```

Result:

```text
20 passed in 0.08s
```

---

## 2. Engineering model

The workbook represents a **simply supported beam carrying a full-span uniformly distributed load**.

### Governing equations

| Quantity | Equation | Meaning |
|---|---|---|
| Maximum bending moment | `M_max = wL² / 8` | Maximum moment for a simply supported beam under full-span UDL |
| Bending stress | `σ = M_max / S` | Extreme-fibre bending stress |
| Utilisation | `U = σ / f_y` | Stress demand divided by yield strength |
| Maximum midspan deflection | `δ_max = 5wL⁴ / (384EI)` | Elastic midspan deflection for the stated beam/load case |
| Allowable deflection | `δ_limit = L / n` | Deflection limit defined by the workbook |
| Stress result | `PASS` if `U ≤ 1` | Stress acceptance criterion |
| Deflection result | `PASS` if `δ_max ≤ δ_limit` | Deflection acceptance criterion |

A checked engineering reference for the simply supported full-span UDL case gives the same moment, stress and deflection relationships:

https://calcs.com/freetools/beam-analysis

### Engineering assumptions

The calculation assumes:

- simply supported beam behaviour;
- a uniformly distributed load acting over the full span;
- constant Young's modulus `E`;
- constant second moment of area `I`;
- supplied section modulus `S` and second moment of area `I` are applicable to the beam;
- linear-elastic, small-deflection beam theory;
- the stress comparison is made against the supplied yield strength `f_y`.

This project validates the identified mathematical model against the stated engineering formulation. It does **not** claim validation against physical test data or a complete structural design code.

---

## 3. Workbook input case

The workbook's pre-filled case is:

| Input | Value | Unit |
|---|---:|---|
| Span, `L` | 6.0 | m |
| Uniform load, `w` | 10.0 | kN/m |
| Section modulus, `S` | 597.0 | cm³ |
| Second moment of area, `I` | 8503.0 | cm⁴ |
| Young's modulus, `E` | 200.0 | GPa |
| Yield strength, `f_y` | 275.0 | MPa |
| Deflection ratio, `n` | 360.0 | — |

---

## 4. Independent calculation of the workbook case

The numerical results below were independently recomputed using SI units.

### Maximum bending moment

```text
M_max = wL² / 8
      = 10 × 6² / 8
      = 45.000000 kN·m
```

### Bending stress

Convert the section modulus:

```text
597 cm³ = 597 × 10⁻⁶ m³
```

Convert the moment:

```text
45 kN·m = 45,000 N·m
```

Therefore:

```text
σ = M / S
  = 45,000 / (597 × 10⁻⁶)
  = 75.376884 MPa
```

### Stress utilisation

```text
U = σ / f_y
  = 75.37688442211055 / 275
  = 0.27409776153494747
```

Since:

```text
U < 1
```

the stress check is:

```text
PASS
```

### Midspan deflection

Using SI units:

```text
w = 10 kN/m = 10,000 N/m
E = 200 GPa = 200 × 10⁹ Pa
I = 8503 cm⁴ = 8503 × 10⁻⁸ m⁴
```

Then:

```text
δ_max = 5wL⁴ / (384EI)

      = 5(10,000)(6⁴)
        / [384(200 × 10⁹)(8503 × 10⁻⁸)]

      = 0.009922968364106787 m

      = 9.922968364106787 mm
```

### Allowable deflection

```text
δ_limit = L / n
        = 6 / 360
        = 0.016666666666666668 m
        = 16.666666666666668 mm
```

Since:

```text
9.922968364 mm < 16.666666667 mm
```

the deflection check is:

```text
PASS
```

---

## 5. Verification against the workbook

The following table maps the workbook outputs to the Python implementation.

| Output | Workbook | Python | Tolerance | Result |
|---|---:|---:|---:|---|
| Maximum moment, `M` | 45.000000 kN·m | 45.000000 kN·m | `1e-12` rel/abs | PASS |
| Bending stress, `σ` | 75.376884 MPa | 75.376884 MPa | `1e-10` rel | PASS |
| Utilisation, `U` | 0.274097762 | 0.274097762 | `1e-10` rel | PASS |
| Midspan deflection, `δ` | 9.922968 mm | 9.922968 mm | `1e-10` rel | PASS |
| Deflection limit | 16.666667 mm | 16.666667 mm | `1e-10` rel | PASS |
| Stress check | PASS | PASS | Exact | PASS |
| Deflection check | PASS | PASS | Exact | PASS |

The tolerances are intentionally tight because these are deterministic closed-form calculations. There is no iterative numerical solver or measured-data uncertainty involved in reproducing the workbook case.

The tests use `pytest.approx` with explicit relative and absolute tolerances.

---

## 6. Undocumented workbook constant

The workbook contains:

```text
Calculation!E2 = 100000
```

This value is used in the workbook's deflection calculation.

It is **not an additional engineering coefficient**. It is a composite unit-conversion factor caused by the workbook's mixed numerical units:

```text
w  → kN/m
L  → m
E  → GPa
I  → cm⁴
δ  → mm
```

For the raw numerical expression:

```text
5wL⁴ / (384EI)
```

the combined conversion required to report the result in millimetres is:

```text
100000
```

Equivalently, the factor accounts for:

- kN → N;
- GPa → Pa;
- cm⁴ → m⁴;
- m → mm.

The Python implementation intentionally does **not** copy this unexplained constant. Instead, it converts all inputs to SI units at the input boundary and performs the calculation in SI base units.

This is clearer, auditable, and avoids embedding a spreadsheet-specific magic number in the production calculation.

---

## 7. Unit handling

### SI input mode

The Python API accepts:

| Input | Unit |
|---|---|
| Span | m |
| Uniform load | kN/m |
| Section modulus | cm³ |
| Second moment of area | cm⁴ |
| Young's modulus | GPa |
| Yield strength | MPa |
| Deflection ratio | dimensionless |

### Imperial input mode

The API accepts:

| Input | Unit |
|---|---|
| Span | ft |
| Uniform load | kip/ft |
| Section modulus | in³ |
| Second moment of area | in⁴ |
| Young's modulus | ksi |
| Yield strength | ksi |
| Deflection ratio | dimensionless |

All calculations are converted to SI base units before the engineering equations are evaluated.

### Conversion factors

The implementation uses the following factors:

| Conversion | Factor |
|---|---:|
| `1 ft` | `0.3048 m` |
| `1 in` | `0.0254 m` |
| `1 kip` | `4448.2216152605 N` |
| `1 in³` | `(0.0254 m)³` |
| `1 in⁴` | `(0.0254 m)⁴` |
| `1 ksi` | `6.894757 × 10⁶ Pa` |

The conversion factors are based on NIST's Guide to the SI, Appendix B conversion factors:

https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8

NIST's tables give, among other values, `1 ft = 0.3048 m`, `1 kip = 4.448222 × 10³ N`, `1 in⁴ = 4.162314 × 10⁻⁷ m⁴`, and `1 ksi = 6.894757 × 10⁶ Pa`.

---

## 8. Verification test coverage

The final `test_beam_check.py` contains **20 pytest cases**.

| Test area | What is checked |
|---|---|
| Workbook regression | Reproduces all pre-filled workbook outputs |
| SI calculation | Checks moment, stress, utilisation, deflection and limit |
| Imperial equivalence | Confirms Imperial inputs produce the same engineering results as SI inputs |
| Non-positive span | Rejects zero and negative span |
| Non-positive load | Rejects zero and negative load |
| Non-positive section modulus | Rejects zero and negative section modulus |
| Non-positive second moment | Rejects zero and negative second moment |
| Non-positive Young's modulus | Rejects zero and negative `E` |
| Non-positive yield strength | Rejects zero and negative `f_y` |
| Non-positive deflection ratio | Rejects zero and negative `n` |
| Invalid unit system | Rejects unsupported unit-system values |
| Stress near boundary | Confirms a value just below utilisation `1.0` passes |
| Stress above boundary | Confirms utilisation above `1.0` fails |
| Deflection boundary | Confirms equality with the deflection limit passes |

Run the suite with:

```bash
python -m pytest -q
```

Expected result for the submitted three files:

```text
20 passed
```

---

## 9. Reproducibility correction

An earlier AI-assisted version had an import/reproducibility issue: the test import path did not reliably match the three-file submission layout.

The test was corrected to import the production module directly:

```python
from beam_check import beam_check
```

The final three files were then placed together and executed from the same directory.

The final command was:

```bash
python -m pytest -q
```

and produced:

```text
....................                                                     [100%]
20 passed
```

No expected value was changed merely to make the tests pass.

---

## 10. AI-assisted development and verification

AI assistance was used during development, but AI output was treated as **unverified input**, not as the authority for the engineering calculation.

### Tools used

| Tool | Use |
|---|---|
| **Claude Sonnet** | Earlier spreadsheet analysis, formula identification, engineering assumptions and unit-handling discussion |
| **OpenAI ChatGPT** | Python implementation, pytest structure, reproducibility review and V&V documentation |
| **GitHub Copilot** | Coding assistance while developing/refactoring Python and pytest |
| **DeepSeek** | Additional reasoning and cross-checking of calculation/implementation approaches |
| **Perplexity** | Finding and checking external engineering and unit-conversion references |

### Most significant AI-assisted issue that was corrected

The most significant issue was **not accepting an AI-generated implementation simply because its output looked plausible**.

The earlier test version had an import path that did not reliably match the three-file submission layout. This was corrected so that the test imports `beam_check` directly from the same directory as the test.

The deflection calculation was also independently checked using SI units:

```text
L = 6 m
w = 10 kN/m
E = 200 GPa
I = 8503 cm⁴
```

which gives:

```text
δ = 0.009922968364106787 m
  = 9.922968364106787 mm
```

This independently agrees with the workbook's `100000` conversion-factor approach.

The final test suite was then executed against the final three-file submission and produced:

```text
20 passed
```

If a future comparison produces an unexplained discrepancy, the correct action is to investigate and report the discrepancy rather than modify the implementation or expected value solely to force agreement.

---

## 11. Validation vs verification summary

| Question | Conclusion |
|---|---|
| Are the equations appropriate for the stated beam/load model? | **Yes** — they match the standard closed-form equations for a simply supported beam under full-span UDL. |
| Does Python reproduce the workbook case? | **Yes** — all numerical outputs agree within explicit tolerances. |
| Are SI and Imperial inputs consistent? | **Yes** — the test suite verifies equivalence. |
| Is the workbook's `100000` an engineering coefficient? | **No** — it is a composite unit-conversion factor. |
| Are invalid inputs handled? | **Yes** — non-positive required inputs raise `ValueError`. |
| Was the implementation tested after correcting the import issue? | **Yes** — `20 passed`. |
| Was AI output accepted without verification? | **No** — important outputs and implementation details were independently checked. |

---

## 12. References

### Engineering equations

Calcs.com, *Free Beam Calculator: Moment, Shear, Deflection*:

https://calcs.com/freetools/beam-analysis

The reference explicitly states the simply supported, uniform-load equations:

```text
M_max = wL² / 8
δ_max = 5wL⁴ / (384EI)
σ = M / S
```

### Unit conversions

NIST, *Guide to the SI, Appendix B: Conversion Factors*:

https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors

### Source workbook

The engineering calculation was derived from the supplied:

```text
source_workbook.xlsx
```

---

## 13. Final status

**Verification status: PASS**

**Validation status: PASS for the stated idealised beam model**

**Automated test status: 20 passed**

The implementation reproduces the supplied workbook case, uses explicit SI conversion at the calculation boundary, supports Imperial/SI equivalence, documents the workbook's unexplained conversion constant, and records the AI-assisted development and verification process transparently.
