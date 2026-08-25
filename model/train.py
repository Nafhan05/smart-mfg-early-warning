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
    
    # Handle kasus dimana tidak ada perubahan (0)
    actual_dir = np.where(actual_dir == 0, 1, actual_dir)
    pred_dir = np.where(pred_dir == 0, 1, pred_dir)
    
    correct_dir = (actual_dir == pred_dir).sum()
    return correct_dir / len(y_true)


def train_model(df: pd.DataFrame, target_col: str, feature_cols: list, test_size=12):
    """Latih model LightGBM untuk memprediksi IHPB."""
    # Data sudah berurutan berdasarkan waktu, jadi kita lakukan time-based split.
    # Kita pisahkan beberapa data terakhir untuk testing
    
    # Hilangkan row dimana target bernilai NaN (misalnya row-row terakhir setelah shift)
    df_clean = df.dropna(subset=[target_col]).copy()
    
    if len(df_clean) <= test_size:
        raise ValueError("Dataset is too small for the given test size")
        
    train_df = df_clean.iloc[:-test_size]
    test_df = df_clean.iloc[-test_size:]
    
    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]
    
    # Base/Current value untuk menghitung directional accuracy
    # (Nilai IHPB saat prediksi dibuat)
    y_test_base = test_df['ihpb_nasional']
    
    print(f"  Training shape: {X_train.shape}, Testing shape: {X_test.shape}")
    
    # Training dengan LightGBM
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'learning_rate': 0.05,
        'num_leaves': 15,
        'max_depth': -1,
        'verbose': -1,
        'random_state': 42
    }
    
    model = lgb.LGBMRegressor(**params, n_estimators=100)
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
    
    # Evaluasi
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    dir_acc = directional_accuracy(y_test.values, y_pred, y_test_base.values)
    
    print(f"  Evaluation - MAE: {mae:.4f}, RMSE: {rmse:.4f}, DirAcc: {dir_acc*100:.2f}%")
    
    return model, feature_cols, mae, rmse, dir_acc


def main():
    """Main training pipeline."""
    print("Loading processed data...")
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
    
    print(f"Selected {len(feature_cols)} features: {feature_cols}")

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
    
    print("Training selesai. Artifacts tersimpan.")


if __name__ == "__main__":
    main()
