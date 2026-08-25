"""
Data Processing Pipeline untuk Sistem Peringatan Dini Biaya Bahan Baku.
Membersihkan data mentah dari data/raw/ dan menyimpan ke data/processed/.

Jalankan: python data/process.py
Hasil:   data/processed/dataset_ready.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys


# ─────────────────────────── Paths ────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent
RAW_DIR = ROOT_DIR / "raw"
PROCESSED_DIR = ROOT_DIR / "processed"

RAW_GABUNGAN = RAW_DIR / "data_gabungan_final.csv"
RAW_IHPB_ALL = RAW_DIR / "ihpb_all_sectors_normalized.csv"
RAW_IHPB_IMPOR = RAW_DIR / "ihpb_impor_normalized.csv"
RAW_IHPB_NASIONAL = RAW_DIR / "ihpb_nasional_normalized.csv"
RAW_KURS = RAW_DIR / "kurs_usd_idr.csv"


def load_raw_data():
    """Load semua file CSV dari data/raw/."""
    print("[1/6] Loading raw data...")
    
    df_gabungan = pd.read_csv(RAW_GABUNGAN)
    df_ihpb_all = pd.read_csv(RAW_IHPB_ALL)
    df_ihpb_impor = pd.read_csv(RAW_IHPB_IMPOR)
    df_ihpb_nasional = pd.read_csv(RAW_IHPB_NASIONAL)
    df_kurs = pd.read_csv(RAW_KURS)
    
    print(f"  data_gabungan_final : {df_gabungan.shape}")
    print(f"  ihpb_all_sectors    : {df_ihpb_all.shape}")
    print(f"  ihpb_impor          : {df_ihpb_impor.shape}")
    print(f"  ihpb_nasional       : {df_ihpb_nasional.shape}")
    print(f"  kurs_usd_idr        : {df_kurs.shape}")
    
    return df_gabungan, df_ihpb_all, df_ihpb_impor, df_ihpb_nasional, df_kurs


def build_master_dataset(df_ihpb_all, df_kurs):
    """
    Bangun dataset master dari sumber individual (lebih reliable
    daripada file gabungan yang sudah punya anomali).
    
    Strategi: rebuild dari file-file terpisah supaya lebih bersih.
    """
    print("[2/6] Building master dataset from individual sources...")
    
    # ── IHPB Nasional (sektor 'IHPB' = indeks umum) ──
    ihpb_nasional = df_ihpb_all[df_ihpb_all["sektor"] == "IHPB"][["periode", "ihpb"]].copy()
    ihpb_nasional = ihpb_nasional.rename(columns={"ihpb": "ihpb_nasional"})
    
    # ── IHPB Industri (paling relevan untuk manufaktur makanan-minuman) ──
    ihpb_industri = df_ihpb_all[df_ihpb_all["sektor"] == "Industri"][["periode", "ihpb"]].copy()
    ihpb_industri = ihpb_industri.rename(columns={"ihpb": "ihpb_industri"})
    
    # ── IHPB Impor ──
    ihpb_impor = df_ihpb_all[df_ihpb_all["sektor"] == "Impor"][["periode", "ihpb"]].copy()
    ihpb_impor = ihpb_impor.rename(columns={"ihpb": "ihpb_impor"})
    
    # ── IHPB Ekspor ──
    ihpb_ekspor = df_ihpb_all[df_ihpb_all["sektor"] == "Ekspor"][["periode", "ihpb"]].copy()
    ihpb_ekspor = ihpb_ekspor.rename(columns={"ihpb": "ihpb_ekspor"})
    
    # ── IHPB Pertanian — DIBUANG ──
    # Data ihpb_pertanian kualitasnya buruk: bernilai 1.0 dari 2021-02
    # sampai 2025-09 (50 baris), sehingga tidak reliable untuk fitur.
    
    # ── Kurs USD/IDR ──
    kurs = df_kurs[["periode", "kurs_tengah", "kurs_jual", "kurs_beli"]].copy()
    
    # ── Merge semua berdasarkan periode ──
    # Mulai dari IHPB nasional sebagai base
    df = ihpb_nasional.copy()
    
    for other_df in [ihpb_industri, ihpb_impor, ihpb_ekspor, kurs]:
        df = df.merge(other_df, on="periode", how="outer")
    
    # Sort by periode
    df = df.sort_values("periode").reset_index(drop=True)
    
    print(f"  Master dataset shape: {df.shape}")
    print(f"  Period range: {df['periode'].min()} to {df['periode'].max()}")
    
    return df


def clean_data(df):
    """
    Bersihkan data: handle anomali, missing values, dan filter periode usable.
    """
    print("[3/6] Cleaning data...")
    
    rows_before = len(df)
    
    # ── Ganti nilai 0 dengan NaN (anomali — IHPB tidak mungkin 0) ──
    ihpb_cols = [c for c in df.columns if c.startswith("ihpb_")]
    for col in ihpb_cols:
        n_zeros = (df[col] == 0).sum()
        if n_zeros > 0:
            print(f"  Replacing {n_zeros} zero(s) in '{col}' with NaN")
            df[col] = df[col].replace(0, np.nan)
    
    # ── Handle rebasing IHPB BPS ──
    # Data IHPB BPS ada diskontinuitas di sekitar 2014:
    #   2014-02: IHPB = 212  (level lama)
    #   2014-03: IHPB = 126  (anomali)
    #   2014-05: IHPB = 189  (anomali)
    #   2014-07: IHPB = 130  (level baru, stabil)
    # Ini bukan outlier biasa, melainkan perubahan basis indeks oleh BPS.
    # Solusi: hanya gunakan data setelah rebasing stabil (2014-07+).
    # Ini mengorbankan ~54 bulan data (2010-01 s/d 2014-06), tapi memastikan
    # bahwa semua data dalam satu skala yang konsisten.
    cutoff_periode = "2014-07"
    rows_cut = (df["periode"] < cutoff_periode).sum()
    df = df[df["periode"] >= cutoff_periode].copy()
    print(f"  Removed {rows_cut} pre-rebase rows (before {cutoff_periode})")
    
    # ── Deteksi outlier IHPB sisa: perubahan > 10% bulan-ke-bulan ──
    # Setelah rebase, pergerakan IHPB normal < 5% per bulan
    for col in ihpb_cols:
        if col in df.columns and df[col].notna().sum() > 10:
            mom_change = df[col].pct_change(fill_method=None).abs()
            outliers = mom_change > 0.10  # > 10% per bulan = anomali
            n_outliers = outliers.sum()
            if n_outliers > 0:
                print(f"  Found {n_outliers} outlier(s) in '{col}' (>10% MoM), replacing with NaN")
                df.loc[outliers, col] = np.nan
    
    # ── Filter: hanya ambil periode dimana IHPB nasional tersedia ──
    # IHPB nasional adalah target utama, jadi kita butuh data ini
    # Data kurs tanpa IHPB tidak berguna untuk training
    df = df.dropna(subset=["ihpb_nasional"]).copy()
    
    rows_after = len(df)
    print(f"  Rows dropped (no ihpb_nasional): {rows_before - rows_after}")
    
    # ── Interpolasi missing values pada kolom lain (linear) ──
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    n_missing_before = df[numeric_cols].isnull().sum().sum()
    
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear", limit_direction="both")
    
    n_missing_after = df[numeric_cols].isnull().sum().sum()
    print(f"  Interpolated {n_missing_before - n_missing_after} missing values")
    
    # ── Drop baris yang masih punya NaN setelah interpolasi ──
    remaining_na = df.isnull().sum().sum()
    if remaining_na > 0:
        print(f"  Dropping {df.isnull().any(axis=1).sum()} rows with remaining NaN")
        df = df.dropna().reset_index(drop=True)
    
    print(f"  Clean dataset: {df.shape}")
    print(f"  Period range: {df['periode'].min()} to {df['periode'].max()}")
    
    return df


def add_derived_features(df):
    """
    Tambahkan fitur turunan: persentase perubahan, bulan, dll.
    """
    print("[4/6] Adding derived features...")
    
    # ── Parse periode ──
    df["year"] = df["periode"].str[:4].astype(int)
    df["bulan"] = df["periode"].str[5:7].astype(int)
    
    # ── Perubahan persen bulan-ke-bulan ──
    for col in ["ihpb_nasional", "ihpb_industri", "ihpb_impor", "kurs_tengah"]:
        if col in df.columns:
            pct_col = f"{col}_pct_change"
            df[pct_col] = df[col].pct_change() * 100
    
    # ── Spread kurs (jual - beli) sebagai indikator volatilitas ──
    if "kurs_jual" in df.columns and "kurs_beli" in df.columns:
        df["kurs_spread"] = df["kurs_jual"] - df["kurs_beli"]
    
    # ── Drop baris pertama (NaN dari pct_change) ──
    df = df.iloc[1:].reset_index(drop=True)
    
    print(f"  Added columns: year, bulan, pct_change cols, kurs_spread")
    print(f"  Dataset shape: {df.shape}")
    
    return df


def create_target_variables(df, target_col="ihpb_nasional", horizons=[1, 2, 3]):
    """
    Buat target variables: IHPB di h bulan ke depan.
    
    target_ihpb_h1 = IHPB di 1 bulan ke depan
    target_ihpb_h2 = IHPB di 2 bulan ke depan
    target_ihpb_h3 = IHPB di 3 bulan ke depan
    """
    print("[5/6] Creating target variables...")
    
    for h in horizons:
        col_name = f"target_ihpb_h{h}"
        df[col_name] = df[target_col].shift(-h)
        
        # Juga buat target perubahan persen
        pct_col_name = f"target_change_pct_h{h}"
        df[pct_col_name] = ((df[col_name] - df[target_col]) / df[target_col]) * 100
        
        # Buat target arah (naik/turun/stabil)
        dir_col_name = f"target_direction_h{h}"
        df[dir_col_name] = "stabil"
        df.loc[df[pct_col_name] > 0.5, dir_col_name] = "naik"
        df.loc[df[pct_col_name] < -0.5, dir_col_name] = "turun"
    
    # Drop baris terakhir yang tidak punya target (karena shift)
    max_horizon = max(horizons)
    rows_before = len(df)
    df = df.iloc[:-max_horizon].reset_index(drop=True)
    print(f"  Dropped {rows_before - len(df)} tail rows (no future target)")
    
    # ── Validasi: drop baris dengan target anomali ──
    # Target IHPB < 50 atau perubahan > 50% jelas anomali
    target_cols = [f"target_ihpb_h{h}" for h in horizons]
    pct_cols = [f"target_change_pct_h{h}" for h in horizons]
    
    anomaly_mask = pd.Series(False, index=df.index)
    for tc in target_cols:
        anomaly_mask |= (df[tc] < 50)
    for pc in pct_cols:
        anomaly_mask |= (df[pc].abs() > 50)
    
    n_anomalies = anomaly_mask.sum()
    if n_anomalies > 0:
        print(f"  Removed {n_anomalies} row(s) with anomalous target values")
        df = df[~anomaly_mask].reset_index(drop=True)
    
    print(f"  Target columns created for horizons: {horizons}")
    print(f"  Final dataset shape: {df.shape}")
    
    return df


def save_processed(df):
    """Simpan dataset bersih ke data/processed/."""
    print("[6/6] Saving processed data...")
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    output_path = PROCESSED_DIR / "dataset_ready.csv"
    df.to_csv(output_path, index=False)
    print(f"  Saved to: {output_path}")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    
    # Juga simpan ringkasan statistik
    stats_path = PROCESSED_DIR / "data_summary.txt"
    with open(stats_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("DATA PROCESSING SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Periode         : {df['periode'].min()} s/d {df['periode'].max()}\n")
        f.write(f"Jumlah baris    : {len(df)}\n")
        f.write(f"Jumlah kolom    : {len(df.columns)}\n")
        f.write(f"Missing values  : {df.isnull().sum().sum()}\n\n")
        
        f.write("KOLOM:\n")
        for col in df.columns:
            dtype = df[col].dtype
            if dtype in [np.float64, np.int64]:
                f.write(f"  {col:30s}  {str(dtype):10s}  "
                        f"min={df[col].min():.2f}  max={df[col].max():.2f}  "
                        f"mean={df[col].mean():.2f}\n")
            else:
                f.write(f"  {col:30s}  {str(dtype):10s}  "
                        f"unique={df[col].nunique()}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("TARGET DISTRIBUTION (horizon 1 bulan):\n")
        f.write("=" * 60 + "\n")
        if "target_direction_h1" in df.columns:
            dist = df["target_direction_h1"].value_counts()
            for val, count in dist.items():
                f.write(f"  {val:10s}: {count:4d} ({count/len(df)*100:.1f}%)\n")
    
    print(f"  Summary saved to: {stats_path}")


def main():
    """Main processing pipeline."""
    print("=" * 60)
    print("DATA PROCESSING PIPELINE")
    print("Smart Manufacturing Early Warning")
    print("=" * 60 + "\n")
    
    # 1. Load data
    df_gabungan, df_ihpb_all, df_ihpb_impor, df_ihpb_nasional, df_kurs = load_raw_data()
    
    # 2. Build master dataset dari sumber individual
    df = build_master_dataset(df_ihpb_all, df_kurs)
    
    # 3. Clean data
    df = clean_data(df)
    
    # 4. Add derived features
    df = add_derived_features(df)
    
    # 5. Create target variables
    df = create_target_variables(df)
    
    # 6. Save
    save_processed(df)
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE!")
    print("=" * 60)
    
    return df


if __name__ == "__main__":
    df = main()
