"""
Script training model prediktif IHPB Bahan Baku.
Jalankan sekali saat development: python train.py
Hasil: model.pkl (artifact yang di-load saat inference)
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import os

from features import build_feature_matrix


def load_processed_data() -> pd.DataFrame:
    """Load data bersih siap training."""
    filepath = Path(__file__).parent.parent / "data" / "processed" / "dataset_ready.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}. Please run data/process.py first.")
    
    df = pd.read_csv(filepath)
    return df


def directional_accuracy(y_true, y_pred, y_baseline):
    """Hitung directional accuracy: apakah prediksi naik/turun sesuai dengan kenyataan"""
    actual_dir = np.sign(y_true - y_baseline)
    pred_dir = np.sign(y_pred - y_baseline)
    
    actual_dir = np.where(actual_dir == 0, 1, actual_dir)
    pred_dir = np.where(pred_dir == 0, 1, pred_dir)
    
    correct_dir = (actual_dir == pred_dir).sum()
    return correct_dir / len(y_true)


def select_features(X_train, y_train, feature_cols, max_features=15):
    """Pilih top-N fitur berdasarkan feature importance dari model ringan."""
    selector = lgb.LGBMRegressor(
        n_estimators=50, num_leaves=8, learning_rate=0.1,
        verbose=-1, random_state=42
    )
    selector.fit(X_train, y_train)
    
    importances = selector.feature_importances_
    indices = np.argsort(importances)[-max_features:]
    selected = [feature_cols[i] for i in indices]
    
    print(f"  Feature selection: {len(feature_cols)} -> {len(selected)} features")
    return selected


def train_model(df: pd.DataFrame, target_col: str, feature_cols: list, test_size=12):
    """Latih model LightGBM untuk memprediksi perubahan IHPB."""
    
    df_clean = df.dropna(subset=[target_col]).copy()
    
    if len(df_clean) <= test_size:
        raise ValueError("Dataset is too small for the given test size")
        
    train_df = df_clean.iloc[:-test_size]
    test_df = df_clean.iloc[-test_size:]
    
    # ── Prediksi PERUBAHAN (pct), bukan level absolut ──
    # Sesuai AGENT_GUIDE §5.4: "prediksi perubahan % dari nilai saat ini
    # (sering lebih stabil untuk time-series pendek)"
    y_train_pct = ((train_df[target_col] - train_df['ihpb_nasional']) / train_df['ihpb_nasional']) * 100
    y_test_pct = ((test_df[target_col] - test_df['ihpb_nasional']) / test_df['ihpb_nasional']) * 100
    
    X_train_all = train_df[feature_cols]
    X_test_all = test_df[feature_cols]
    
    # ── Feature selection: kurangi dari ~48 ke ~15 fitur ──
    selected_features = select_features(X_train_all, y_train_pct, feature_cols, max_features=15)
    
    X_train = train_df[selected_features]
    X_test = test_df[selected_features]
    
    y_test_base = test_df['ihpb_nasional'].values
    y_test_actual = test_df[target_col].values
    
    print(f"  Training shape: {X_train.shape}, Testing shape: {X_test.shape}")
    
    # ── Training LightGBM dengan regularisasi kuat ──
    # Dataset kecil (114 baris) butuh regularisasi agresif
    model = lgb.LGBMRegressor(
        objective='regression',
        boosting_type='gbdt',
        n_estimators=200,
        learning_rate=0.03,
        num_leaves=8,           # Sangat kecil — hindari overfitting
        min_child_samples=10,   # Min data per leaf
        subsample=0.7,          # Bagging
        colsample_bytree=0.7,   # Feature bagging
        reg_alpha=0.5,          # L1 regularization
        reg_lambda=1.0,         # L2 regularization
        verbose=-1,
        random_state=42
    )
    model.fit(X_train, y_train_pct, eval_set=[(X_test, y_test_pct)])
    
    # ── Evaluasi: konversi prediksi pct ke absolut ──
    y_pred_pct = model.predict(X_test)
    y_pred_abs = y_test_base * (1 + y_pred_pct / 100)
    
    mae = mean_absolute_error(y_test_actual, y_pred_abs)
    rmse = root_mean_squared_error(y_test_actual, y_pred_abs)
    dir_acc = directional_accuracy(y_test_actual, y_pred_abs, y_test_base)
    
    # Naive baseline
    naive_mae = mean_absolute_error(y_test_actual, y_test_base)
    
    print(f"  MAE: {mae:.4f} (naive: {naive_mae:.4f}) | RMSE: {rmse:.4f} | DirAcc: {dir_acc*100:.1f}%")
    
    return model, selected_features, mae, rmse, dir_acc


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("MODEL TRAINING PIPELINE")
    print("Smart Manufacturing Early Warning")
    print("=" * 60)
    
    print("\nLoading processed data...")
    try:
        df = load_processed_data()
    except FileNotFoundError as e:
        print(e)
        return

    print("Building feature matrix...")
    df_feat = build_feature_matrix(df)
    
    # Features tidak boleh mengandung target atau variabel dari masa depan
    exclude_cols = ['periode', 'year', 'target_ihpb_h1', 'target_change_pct_h1', 'target_direction_h1',
                    'target_ihpb_h2', 'target_change_pct_h2', 'target_direction_h2',
                    'target_ihpb_h3', 'target_change_pct_h3', 'target_direction_h3']
                    
    feature_cols = [c for c in df_feat.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_feat[c])]
    
    print(f"Available features: {len(feature_cols)}")

    print("\nTraining models for different horizons...")
    models = {}
    
    for h in [1, 2, 3]:
        print(f"\n--- Horizon: {h} Bulan ---")
        target_col = f'target_ihpb_h{h}'
        model, features, mae, rmse, dir_acc = train_model(df_feat, target_col, feature_cols, test_size=12)
        
        models[f'horizon_{h}'] = {
            'model': model,
            'features': features,
            'mae': mae,
            'rmse': rmse,
            'dir_acc': dir_acc
        }
    
    # Simpan model
    model_path = Path(__file__).parent / "model.pkl"
    print(f"\nSaving models to {model_path}...")
    joblib.dump(models, model_path)
    
    print("\nTraining selesai. Artifacts tersimpan.")


if __name__ == "__main__":
    main()
