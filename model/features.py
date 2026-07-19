"""
Feature engineering untuk model prediktif IHPB.
Fungsi-fungsi di sini dipakai ulang saat inference (bukan cuma training).
"""

import pandas as pd
import numpy as np


def create_lag_features(df: pd.DataFrame, col: str, lags: list = [1, 3, 6]) -> pd.DataFrame:
    """Buat lag features dari kolom tertentu."""
    # TODO: implementasi oleh P2 (ML Engineer)
    raise NotImplementedError


def create_rolling_features(df: pd.DataFrame, col: str, windows: list = [3]) -> pd.DataFrame:
    """Buat rolling mean & std features."""
    # TODO: implementasi oleh P2 (ML Engineer)
    raise NotImplementedError


def create_seasonal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Buat fitur musiman (bulan, flag Lebaran/Nataru)."""
    # TODO: implementasi oleh P2 (ML Engineer)
    raise NotImplementedError


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Gabungkan semua feature engineering jadi satu pipeline."""
    # TODO: implementasi oleh P2 (ML Engineer)
    raise NotImplementedError
