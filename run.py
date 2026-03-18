import argparse
import json
import logging
import time
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yaml


def setup_logging(log_file: str) -> logging.Logger:
    logger = logging.getLogger("mlops-task")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    fh = logging.FileHandler(log_file)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger


def write_metrics(output_path: str, payload: dict):
    with open(output_path, "w") as f:
        print(json.dumps(metrics))


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    required = ["seed", "window", "version"]
    for key in required:
        if key not in cfg:
            raise ValueError(f"Missing required config field: '{key}'")

    if not isinstance(cfg["seed"], int):
        raise ValueError("Config 'seed' must be an integer")
    if not isinstance(cfg["window"], int) or cfg["window"] < 1:
        raise ValueError("Config 'window' must be a positive integer")

    return cfg


def load_dataset(input_path: str) -> pd.DataFrame:
    if not pd.io.common.file_exists(input_path):
        raise FileNotFoundError(f"Input file not found: '{input_path}'")

    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("Input CSV is empty")
    if "close" not in df.columns:
        raise ValueError("Required column 'close' not found in dataset")

    return df


def compute_signals(df: pd.DataFrame, window: int) -> pd.DataFrame:
    df["rolling_mean"] = df["close"].rolling(window=window).mean()

    valid = df["rolling_mean"].notna()
    df.loc[valid, "signal"] = (
        df.loc[valid, "close"] > df.loc[valid, "rolling_mean"]
    ).astype(int)

    return df, valid.sum()


def run(args):
    logger = setup_logging(args.log_file)
    start_time = time.time()
    logger.info(f"Job started at {datetime.now(timezone.utc).isoformat()}Z")

    version = "unknown"

    try:
        logger.info(f"Loading config from: {args.config}")
        cfg = load_config(args.config)
        version = cfg["version"]
        seed = cfg["seed"]
        window = cfg["window"]
        logger.info(f"Config loaded — version={version}, seed={seed}, window={window}")

        np.random.seed(seed)
        logger.info(f"Random seed set to {seed}")

        logger.info(f"Loading dataset from: {args.input}")
        df = load_dataset(args.input)
        rows_loaded = len(df)
        logger.info(f"Dataset loaded — {rows_loaded} rows, columns: {list(df.columns)}")

        logger.info(f"Computing rolling mean with window={window}")
        df, rows_processed = compute_signals(df, window)
        rows_processed = int(rows_processed)
        signal_rate = round(float(df["signal"].mean()), 4)
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Signal generated — signal_rate={signal_rate}, rows_processed={rows_processed}")

        metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": signal_rate,
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }
        write_metrics(args.output, metrics)
        logger.info(f"Metrics written to {args.output}")
        logger.info(f"Job completed successfully. Status: success")

        print(json.dumps(metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Job failed: {e}", exc_info=True)

        error_payload = {
            "version": version,
            "status": "error",
            "error_message": str(e)
        }
        write_metrics(args.output, error_payload)
        print(json.dumps(error_payload, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MLOps batch signal pipeline")
    parser.add_argument("--input",    required=True, help="Path to input CSV")
    parser.add_argument("--config",   required=True, help="Path to config YAML")
    parser.add_argument("--output",   required=True, help="Path to output metrics JSON")
    parser.add_argument("--log-file", required=True, help="Path to log file")
    args = parser.parse_args()
    run(args)