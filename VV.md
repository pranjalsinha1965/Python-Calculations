# Verification & Validation

## Validation — are these the right equations?

The source workbook models a simply supported beam under a uniformly distributed load.
The workbook equations are:

- `M = wL^2 / 8`
- `sigma = M / S`
- `utilisation = sigma / fy`
- `delta = 5wL^4 / (384EI)`
- `deflection limit = L / n`

The final submission should cite checked engineering references for these equations and
state the assumptions under which elementary beam theory applies.

## Verification — does the code solve them correctly?

The pre-filled workbook inputs are:

`L=6 m, w=10 kN/m, S=597 cm^3, I=8503 cm^4, E=200 GPa, fy=275 MPa, n=360`.

| Output           | Expected value | Tolerance |
|------------------|----------------|-----------|
| M                | 45.0 kN·m      | abs 1e-12 |
| sigma            | 75.376884 MPa  | rel 1e-10 |
| utilisation      | 0.27409776     | rel 1e-10 |
| delta            | 9.922968 mm    | rel 1e-10 |
| limit            | 16.666667 mm   | rel 1e-10 |
| stress check     | PASS | exact   |           |
| deflection check | PASS | exact   |           |

Tests also cover Imperial/SI equivalence, a stress PASS boundary, and invalid inputs.

## Discrepancy / undocumented constant

The workbook's deflection formula references an unlabeled value `100000`. This is an
undocumented compound unit-conversion multiplier resulting from the workbook's mixed
units. The Python implementation does not copy this magic number; it converts inputs
explicitly to SI base units before calculating deflection.

If an unresolved discrepancy remains, it should be documented explicitly rather than
forcing the code to match the workbook.

## AI use

AI assistance was used for workbook analysis, drafting code, tests and documentation.
Outputs were checked against the workbook. The most significant item requiring checking
was the unexplained `100000` deflection multiplier; it was replaced by explicit unit
conversion rather than retained as a magic constant.
