# Research reproducibility package

Manuscript: Evaluator constrained evolutionary scheduling for metropolitan driverless transit.

The Word manuscript has approximately 6,600 words including references and captions,
20 references dated 2018–2026, and six original diagrams or simulation figures.
It is a research draft, not an accepted or Scopus-indexed publication.

## Reproduce
Python 3.10+ runs the simulation. Install numpy and matplotlib to create figures.
1. python run_experiments.py
2. python make_figures.py

The first script writes results.csv, training.json, traces.json and manifest.json.
The second writes summary.json, paired_intervals.json, sensitivity.csv and figures.
The original source is retained in source/transit.py.
The original interactive application is included under simulator_application.
Run python server.py from that directory; open http://127.0.0.1:8765.

Training: three demand seeds, five search seeds, 32 unique candidates per run.
Test: twenty demand seeds in three scenarios. Total main calls: 2580.
Diagnostic grid: 81 calls. Trace exports: three calls.
No external LLM was called and no LLM superiority is claimed.

The model is synthetic and uncalibrated. All fifteen searches retain the fixed
incumbent. Identical selected policies are not independent evidence of equivalence.
The supplied manually entered JSON policy is never described as an LLM output.

## Before journal submission
- Confirm author affiliation, declarations, funding and contributor statements.
- Deposit an immutable code/data archive with a public DOI.
- Obtain operator data and calibrate dwell, traction energy, topology and initial state.
- Add platform, junction and turnback feasibility, stateful receding-horizon decisions,
  fleet failures and reserve insertion before claiming those functions.
- Run a genuine logged LLM comparison and matched inference/evaluation budgets if
  retaining LLM assistance as the central empirical contribution.
- Expand scenarios and independent training replicates; predefine meaningful effects.
- Validate time-step sensitivity and energy preference weights.
- Check the current target journal's scope, Scopus coverage and year/category quartile.

The current manuscript provides an honest model-audit and feasibility contribution.
Its present evidence does not justify calling it a publication-ready Q1 breakthrough.
Peer review, scope fit, novelty assessment and acceptance are independent decisions.
