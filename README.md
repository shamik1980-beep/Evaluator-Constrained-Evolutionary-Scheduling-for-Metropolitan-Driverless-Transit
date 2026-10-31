# Metro Evolution Lab

Python 3.10+ required. No third-party packages needed for the server or simulator.

1. Extract the ZIP.
2. In its folder run: python server.py
3. Open http://127.0.0.1:8765
4. Stop with Ctrl+C.

For notebook use, install JupyterLab: python -m pip install jupyterlab
Then run: jupyter lab Metro_Transit_Simulation.ipynb
The notebook embeds and writes all application sources into metro_runtime.

Run verification: python -m unittest -v test_transit

This is an executable research prototype, not certified operational software.
Single bidirectional line; synthetic demand; conservative segment occupancy.
No junctions, transfers, reserves, failures, rolling-horizon state carryover or CP-SAT.
Energy is an uncalibrated proxy. No external LLM calls are made: optional validated
JSON rule import is supported. Evolution tunes bounded rule parameters.
Do not describe evaluation results as proof of production safety or superiority.
Use the notebook for assumptions, experiment design and extension roadmap.

The dashboard requires the Python server; opening index.html directly cannot run
Python simulations. The local server is intentionally not publicly accessible.
