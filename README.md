![CI](https://github.com/ManoRakshithaa/trading-signal-pipeline/actions/workflows/ci.yml/badge.svg)

# Trading Signal Pipeline

A minimal MLOps-style batch job that processes OHLCV cryptocurrency price data and generates binary trading signals using a rolling mean strategy. Built to demonstrate reproducibility, observability, and deployment readiness.

## Tech Stack

- **Python 3.9** — core pipeline logic
- **Pandas** — data loading and rolling mean computation
- **NumPy** — deterministic seeding for reproducible runs
- **PyYAML** — config management
- **Docker** — containerized, one-command execution
- **GitHub Actions** — CI pipeline that auto-builds and validates on every push

## How it works

1. Loads OHLCV price data from CSV
2. Reads configuration from YAML (seed, window, version)
3. Computes a rolling mean on the `close` price
4. Generates a binary signal per row:
   - `1` if close > rolling mean (bullish)
   - `0` if close ≤ rolling mean (bearish)
5. Writes structured metrics to JSON and detailed logs to file

## Project structure
```
trading-signal-pipeline/
├── run.py            # main pipeline script
├── config.yaml       # pipeline configuration
├── data.csv          # input OHLCV dataset (10,000 rows)
├── requirements.txt  # python dependencies
├── Dockerfile        # container definition
├── validate.py       # CI output validator
├── metrics.json      # sample output from successful run
├── run.log           # sample log from successful run
└── .github/
    └── workflows/
        └── ci.yml    # GitHub Actions CI pipeline
```

## Quickstart

### Run locally
```bash
pip install -r requirements.txt

python run.py \
  --input data.csv \
  --config config.yaml \
  --output metrics.json \
  --log-file run.log
```

### Run with Docker
```bash
docker build -t mlops-task .
docker run --rm mlops-task
```

## Configuration

| Field   | Value | Description                     |
|---------|-------|---------------------------------|
| seed    | 42    | random seed for reproducibility |
| window  | 5     | rolling mean lookback window    |
| version | v1    | pipeline version tag            |

## Example output

`metrics.json`:
```json
{
  "version": "v1",
  "rows_processed": 9996,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 12,
  "seed": 42,
  "status": "success"
}
```

`run.log`:
```
2026-03-18T17:08:20 [INFO] Job started at 2026-03-18T17:08:20.290461+00:00Z
2026-03-18T17:08:20 [INFO] Config loaded — version=v1, seed=42, window=5
2026-03-18T17:08:20 [INFO] Dataset loaded — 10000 rows
2026-03-18T17:08:20 [INFO] Signal generated — signal_rate=0.4991, rows_processed=9996
2026-03-18T17:08:20 [INFO] Job completed successfully. Status: success
```

## CI/CD

Every push to `main` automatically:
1. Builds the Docker image on a fresh Linux runner
2. Runs the container
3. Validates the JSON output is correct and deterministic
