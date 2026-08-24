# Take-home task — Software Engineer I

Thanks for your time so far. This task mirrors the actual day job: converting an Excel engineering calculation into verified Python. Budget **2–4 hours**. If you hit 4 hours, stop and note what's unfinished — a clean partial with honest notes beats a rushed complete.

## The calculation

`source_workbook.xlsx` checks a simply-supported steel beam under a uniform load: a bending-stress check and a midspan-deflection check. You don't need a structural-engineering background, but working out **what the spreadsheet computes is part of the task**. The formulas are in the cells and every quantity is labelled with its units; these are standard textbook checks. Read the formulas out of the workbook, find the engineering references they correspond to, and cite what you used — a textbook, a design code, a URL, anything we can check.

Read the spreadsheet carefully: **it contains at least one undocumented hard-coded constant. Identify it, work out what it is, and document it.**

## Deliverables

1. **`beam_check.py`** — a Python module with a function that takes the workbook's inputs and returns the workbook's outputs (M, σ, utilisation, δ, limit, and the two PASS/FAIL results). Requirements:
   - **Imperial input option**: accept inputs in ft / kip/ft / in³ / in⁴ / ksi, convert at the input boundary, compute in SI, report both. Look up the conversion factors yourself; state the values you used and where they came from.
   - Invalid inputs (zero or negative span, load, section properties) raise `ValueError`.
   - **Structure the code however you judge best** — write it the way you write real production code. One constraint to design for: downstream, a deterministic parser reads this code to build a UI, so it must be able to infer the inputs, the calculation steps and the outputs from your code. Explicit symbols and units in names and docstrings help it — and us.
2. **`test_beam_check.py`** — pytest. Use explicit tolerances (`pytest.approx`). Choose your test points; we're interested in *which* points you choose.
3. **`VV.md`** — max one page, treating verification and validation distinctly, in the NAFEMS senses of the words.
   - **Validation — are these the right equations?** The governing formulas you identified from the workbook, the references you checked them against, and the assumptions under which they apply.
   - **Verification — does your code solve them correctly?** A table mapping each of your outputs to the workbook's value for the workbook's pre-filled inputs, the tolerance you used and why, and — honestly — any discrepancy you found and what you did about it. If something doesn't match and you can't resolve it, *saying so clearly* scores better than making it match.

## AI policy

Use any AI tools you like — we do, daily. We're not grading whether you used AI; we're grading whether **you** verified what it gave you. In `VV.md` (or a separate note), tell us:

- which tools you used, and for what — identifying the formulas, writing the code, the tests, this note;
- the most significant thing you had to check, correct or reject from an AI's output, and how you checked it. (If you used no AI, say so — that's fine too.)

If your tool makes it easy to export your prompts or session, feel free to include it — we'd find it interesting, but it's optional and not scored.

## Submission

Reply to the email this brief arrived with, attaching a zip of the three files (plus anything else you think belongs) or a link to a GitHub repo, by the deadline given in that email. Questions about the brief are welcome the same way — just reply; asking a sharp question costs you nothing.
