"""
Feature engineering untuk model prediktif IHPB.
Fungsi-fungsi di sini dipakai ulang saat inference (bukan cuma training).
"""

import pandas as pd
import numpy as np


def create_lag_features(df: pd.DataFrame, col: str, lags: list = [1, 2, 3]) -> pd.DataFrame:
    """Buat lag features dari kolom tertentu."""
    df_out = df.copy()
    for lag in lags:
        df_out[f'{col}_lag_{lag}'] = df_out[col].shift(lag)
    return df_out


def create_rolling_features(df: pd.DataFrame, col: str, windows: list = [3, 6]) -> pd.DataFrame:
    """Buat rolling mean & std features."""
    df_out = df.copy()
    for window in windows:
        # Menghitung rolling mean & std, menggunakan shift supaya 
        # kita tidak melihat masa depan pada baris yang sama.
        # Saat melakukan iterasi feature engineering pada inference, baris terakhir
        # (yang akan diprediksi masa depannya) belum tentu tahu nilai bulan ini (kecuali diberikan)
        # Tapi karena prediksi kita didasarkan pada data "current_index" = t, kita bisa roll dari t.
        df_out[f'{col}_rolling_mean_{window}'] = df_out[col].rolling(window=window).mean()
        df_out[f'{col}_rolling_std_{window}'] = df_out[col].rolling(window=window).std()
    return df_out


def create_seasonal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Buat fitur musiman (bulan, flag Lebaran/Nataru)."""
    df_out = df.copy()
    
    # Ekstrak bulan jika periode berupa string YYYY-MM
    if 'periode' in df_out.columns and 'bulan' not in df_out.columns:
        df_out['bulan'] = pd.to_datetime(df_out['periode']).dt.month
        
    if 'bulan' in df_out.columns:
        # Encode bulan sebagai siklikal agar ML mengerti bahwa Jan(1) dekat dengan Des(12)
        df_out['bulan_sin'] = np.sin(2 * np.pi * df_out['bulan'] / 12)
        df_out['bulan_cos'] = np.cos(2 * np.pi * df_out['bulan'] / 12)
        
        # Flag Nataru (Natal & Tahun Baru) biasanya Desember dan Januari (12, 1)
        df_out['is_nataru'] = df_out['bulan'].apply(lambda x: 1 if x in [12, 1] else 0)
        
    return df_out


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Gabungkan semua feature engineering jadi satu pipeline."""
    df_feat = df.copy()
    
    # 1. Seasonal features
    df_feat = create_seasonal_features(df_feat)
    
    # 2. Lag & Rolling features untuk prediktor utama
    cols_to_lag = ['ihpb_nasional', 'ihpb_industri', 'ihpb_impor', 'kurs_tengah']
    
    # Hanya proses kolom yang ada di dataframe
    cols_to_lag = [c for c in cols_to_lag if c in df_feat.columns]
    
    for col in cols_to_lag:
        df_feat = create_lag_features(df_feat, col, lags=[1, 2, 3, 6])
        df_feat = create_rolling_features(df_feat, col, windows=[3, 6])
        
    # 3. Drop baris yang memiliki NaN akibat Lag/Rolling (saat training)
    # Catatan: Saat inference untuk 1 baris, kita mungkin perlu pass data historis
    # atau mengisi lag NaNs (meski XGB/LGBM bisa handle NaNs)
    
    # Tambahkan fitur perubahan persen jika belum ada
    if 'ihpb_nasional' in df_feat.columns and 'ihpb_nasional_pct_change' not in df_feat.columns:
        df_feat['ihpb_nasional_pct_change'] = df_feat['ihpb_nasional'].pct_change() * 100
    
    return df_feat
