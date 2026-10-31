# Driverless Metropolitan Transit Simulation and Evolutionary Scheduling

A Python research project exploring how scheduling policies affect passenger waiting times, congestion, and estimated energy consumption in a metropolitan driverless rapid transit system.

The project models a synthetic metro line operating in two directions. It simulates passenger arrivals, train movements, station queues, and disruptions such as sudden passenger surges and temporary track speed restrictions. It compares fixed and demand-responsive scheduling policies with random search, genetic algorithms, and evolutionary search enhanced by local refinement.

## Features

- **Self-contained Jupyter notebook** containing the complete simulator and project code.
- **Interactive HTML dashboard** with animated train playback, configurable scenarios, and performance indicators.
- **Evolutionary optimisation** of dispatch intervals, terminal crowd response, dwell extensions, and an illustrative energy parameter.
- **Constraint checks** for train capacity and directed-track-section occupancy.
- **Reproducible experiments** using separate training and test seeds, matched evaluation budgets, and baseline comparisons.
- **CSV datasets and exports** covering synthetic passenger demand, train movements, queues, policies, and experimental results.
- **Optional LLM proposal interface** accepting validated JSON parameters without executing generated Python code.

## Research and Teaching Connection

The project connects concepts from **CSCU9YE — Artificial Intelligence**, particularly rational decision-making, optimisation, heuristic search, local search, evolutionary algorithms, constraint handling, and scientific evaluation.

It provides a practical foundation for studying how AI methods can support transport planning and for investigating future LLM-assisted scheduling policies.

## Getting Started

Install the notebook dependencies:

```bash
pip install jupyterlab numpy matplotlib ipython
```

Launch JupyterLab:

```bash
jupyter lab Driverless_Transit_Complete_Project.ipynb
```

Run the notebook cells in order. To launch the browser dashboard, execute:

```python
start_dashboard()
```

Then open **http://127.0.0.1:8765**.

## Current Findings and Scope

The initial research experiment includes **1,440 training simulations and 1,140 test simulations**. All evaluated search methods retained the seeded fixed policy, highlighting the importance of policy representation, simulator assumptions, and objective design.

The simulator uses synthetic data and an uncalibrated energy proxy. It is a research and teaching prototype, with one bidirectional line and no platform conflicts, junctions, transfers, or certified train-control functions. Live LLM experiments and operational railway integration remain future work.
