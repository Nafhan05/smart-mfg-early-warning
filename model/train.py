"""
Script training model prediktif IHPB Bahan Baku.
Jalankan sekali saat development: python train.py
Hasil: model.pkl (artifact yang di-load saat inference)
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_processed_data(path: str = "../data/processed/") -> pd.DataFrame:
    """Load data bersih siap training."""
    # TODO: implementasi oleh P2 (ML Engineer)
    raise NotImplementedError


def train_model(df: pd.DataFrame, target_col: str, horizon: int = 1):
    """Latih model gradient boosting untuk prediksi IHPB."""
    # TODO: implementasi oleh P2 (ML Engineer)
    # - Time-based split
    # - Train LightGBM/XGBoost
    # - Simpan model ke model.pkl
    raise NotImplementedError


def main():
    """Main training pipeline."""
    print("Loading processed data...")
    df = load_processed_data()

    print("Training model...")
    # TODO: train untuk horizon 1, 2, 3 bulan

    print("Training selesai. Model tersimpan di model/model.pkl")


if __name__ == "__main__":
    main()
