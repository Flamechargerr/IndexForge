# IndexForge ⚙️📈

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**IndexForge** is a robust, rule-based equity index construction and semi-annual rebalancing engine built in Python. Designed to mirror MSCI Cap-Weighted Index methodologies, the engine mathematically processes market-capitalizations, adjusts for free-float factors, filters for trading liquidity screens, and backtests performance against benchmarks automatically.

## 🚀 Key Features

*   **Algorithmic Concept Execution**: Fully automated universe ingestion tracking up to 500+ constituents mirroring major global indices.
*   **Methodology Rulesets**: Implements rigorous financial logic including free-float adjustment modeling and Average Daily Traded Volume (ADTV) liquidity screenings.
*   **Automated Rebalancing Engine**: Simulates semi-annual execution. Contains proprietary retention buffer-zones to dramatically minimize portfolio turnover while achieving size-focused target ranks. 
*   **Performance Attribution**: Generates end-to-end comparative backtesting metrics versus proxy benchmarks (like the `SPY`), explicitly surfacing sector allocation drift trajectories and historical constituent weight vectors.
*   **Resilient Database Integrations**: Built atop an SQLAlchemy ORM mapping, ingesting data automatically into a normalized relational (SQL) layer.
*   **Failover Handling**: Integrated synthetic geometric brownian motion fail-proof mechanisms preventing upstream rate-limit execution blockers.

## 🛠 Tech Stack
*   **Language**: `Python 3`
*   **Data Pipelines**: `pandas`, `NumPy`, `yfinance`
*   **Database**: `SQLAlchemy`, `SQLite` (Easily scalable to `PostgreSQL` via connection string swaps)
*   **Reporting**: `tabulate`, automated markdown attribution generators

---

## 💻 Getting Started

### 1. Environment Setup

Ensure you are using Python 3.9+. It is highly recommended to isolate the project within a virtual environment.

```bash
git clone https://github.com/flamechargerr/IndexForge.min.git
cd IndexForge

# Create and activate a Virtual Environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install strictly typed dependencies
pip install -r requirements.txt
```

### 2. Execution Pipeline

The platform is driven sequentially via a robust CLI (`main.py`).

**Step 1: Initialize Database Schema**
```bash
python main.py --setup
```

**Step 2: Ingest the Market Data Universe**
*Downloads market metrics and 5-year historical pricing for the constituent universe directly into the SQL models.*
```bash
python main.py --ingest
```

**Step 3: Run Math & Rebalancing Engines**
*Calculates targeted constituent weights, executes the sector boundary math, transitions divisors, and traces the daily composite value.*
```bash
python main.py --run-engine
```

**Step 4: Generate Attribution Report**
*Compares tracking histories and dumps turnover + drift metrics.*
```bash
python main.py --backtest
```

The comprehensive portfolio breakdown will be dumped into `indexforge_report.md` at the root directory!

## 📈 System Architecture Snippets

The implementation separates index derivation into strict modules:

*   `data_ingestion/db_loader.py`: Chunked multi-batch insertion utilities scaling effortlessly beyond memory limits.
*   `index_math/rebalancing.py`: Execution of deterministic buffer rules, checking constituent threshold boundaries.
*   `backtesting/attribution.py`: Grouping allocations mathematically to extrapolate sector bias drifts organically occurring between structural fixes.

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
