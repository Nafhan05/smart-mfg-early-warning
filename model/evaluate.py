"""
Script evaluasi & backtesting model prediktif IHPB.
Metrik: MAE, RMSE, directional accuracy.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Hitung metrik evaluasi: MAE, RMSE, directional accuracy."""
    # TODO: implementasi oleh P2 (ML Engineer)
    raise NotImplementedError


def directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray, y_baseline: np.ndarray) -> float:
    """Hitung seberapa sering arah naik/turun diprediksi benar."""
    # TODO: implementasi oleh P2 (ML Engineer)
    raise NotImplementedError


def backtest(model, df: pd.DataFrame, horizon: int = 1) -> dict:
    """Backtest model terhadap data historis."""
    # TODO: implementasi oleh P2 (ML Engineer)
    raise NotImplementedError


def main():
    """Jalankan evaluasi pada model yang sudah di-training."""
    print("Loading model dan data...")
    # TODO: load model.pkl dan data test

    print("Menjalankan backtesting...")
    # TODO: jalankan backtest

    print("Hasil evaluasi:")
    # TODO: print hasil MAE, RMSE, directional accuracy


if __name__ == "__main__":
    main()
