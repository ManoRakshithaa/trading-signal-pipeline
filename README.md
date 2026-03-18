# Trading Signal Pipeline

A minimal MLOps-style batch job that computes a binary trading signal from OHLCV data using a rolling mean strategy.

## What it does

- Loads OHLCV price data from CSV
- Computes a rolling mean on the `close` price
- Generates a binary signal: `1` if close > rolling mean, else `0`
- Outputs structured metrics JSON and detailed logs
- Fully reproducible via config seed

## Project structure
```
trading-signal-pipeline/
├── run.py            # main pipeline script
├── config.yaml       # pipeline configuration
├── data.csv          # input OHLCV dataset (10,000 rows)
├── requirements.txt  # python dependencies
├── Dockerfile        # container definition
├── metrics.json      # sample output from successful run
└── run.log           # sample log from successful run
```

## Local run

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the pipeline:
```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

## Docker

Build the image:
```bash
docker build -t mlops-task .
```

Run the container:
```bash
docker run --rm mlops-task
```

## Example metrics.json
```json
{
  "version": "v1",
  "rows_processed": 9996,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 8,
  "seed": 42,
  "status": "success"
}
```

## Config

| Field   | Value | Description                        |
|---------|-------|------------------------------------|
| seed    | 42    | random seed for reproducibility    |
| window  | 5     | rolling mean lookback window       |
| version | v1    | pipeline version tag               |