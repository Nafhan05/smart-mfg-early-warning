import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
import sys

# Tambahkan path root untuk meng-import features.py
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from model.features import build_feature_matrix


class Predictor:
    def __init__(self):
        self.models = None
        self.load_model()
        self.dataset_ready = self.load_data()

    def load_model(self):
        default_path = Path(__file__).parent.parent / "model" / "model.pkl"
        model_path = Path(os.getenv("MODEL_PATH", str(default_path)))
        if model_path.exists():
            self.models = joblib.load(model_path)
            print("Models loaded successfully.")
        else:
            print(f"Warning: Model not found at {model_path}. Please run train.py first.")
            self.models = None
            
    def load_data(self):
        default_path = Path(__file__).parent.parent / "data" / "processed" / "dataset_ready.csv"
        data_path = Path(os.getenv("DATA_PATH", str(default_path)))
        if data_path.exists():
            return pd.read_csv(data_path)
        else:
            print(f"Warning: Data not found at {data_path}.")
            return None

    def predict(self, sector: str, horizon_months: int, mode: str = "latest", sample_period: str | None = None):
        """
        Lakukan prediksi untuk sektor tertentu sejauh horizon_months ke depan.

        mode="latest"   : prediksi dari data terbaru (baris terakhir dataset).
        mode="backtest" : prediksi dari contoh historis (sample_period, format YYYY-MM),
                          lalu dibandingkan dengan nilai aktualnya.
        """
        if self.models is None or self.dataset_ready is None:
            raise RuntimeError("Model or Data not loaded.")
            
        model_key = f"horizon_{horizon_months}"
        if model_key not in self.models:
            raise ValueError(f"Model for horizon {horizon_months} not available.")
            
        model_data = self.models[model_key]
        model = model_data['model']
        features = model_data['features']
        
        # Buat feature matrix menggunakan fungsi dari model/features.py
        df_feat = build_feature_matrix(self.dataset_ready)

        # Tentukan baris dasar (latest atau backtest)
        actual_index = None
        if mode == "backtest":
            if not sample_period:
                raise ValueError("sample_period wajib diisi untuk mode backtest (format YYYY-MM).")
            matches = self.dataset_ready.index[self.dataset_ready["periode"] == sample_period]
            if len(matches) == 0:
                raise ValueError(f"Periode {sample_period} tidak ditemukan di dataset.")
            idx = matches[0]
            df_latest = self.dataset_ready.iloc[[idx]].copy()
            df_feat_latest = df_feat.iloc[[idx]]
            actual_index = df_latest[f"target_ihpb_h{horizon_months}"].values[0]
            if pd.isna(actual_index):
                raise ValueError(
                    f"Tidak ada nilai aktual untuk periode {sample_period} dengan horizon {horizon_months} bulan."
                )
        else:
            df_latest = self.dataset_ready.tail(1).copy()
            df_feat_latest = df_feat.tail(1)

        # Ambil feature yang sesuai dengan waktu training
        X = df_feat_latest[features]
        
        # Nilai IHPB saat ini
        current_index = df_latest['ihpb_nasional'].values[0]
        
        # Predict — model menghasilkan pct_change, bukan level absolut
        predicted_change_pct = model.predict(X)[0]
        
        # Konversi ke level absolut
        predicted_index = current_index * (1 + predicted_change_pct / 100)
        
        # Arah
        direction = "stabil"
        if predicted_change_pct > 0.5:
            direction = "naik"
        elif predicted_change_pct < -0.5:
            direction = "turun"
            
        # Dapatkan fitur yang paling berpengaruh berdasarkan LightGBM feature importances
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        top_features = [features[i] for i in indices[:3]]

        result = {
            "current_index": float(current_index),
            "predicted_index": float(predicted_index),
            "predicted_change_pct": float(predicted_change_pct),
            "direction": direction,
            "top_features": top_features,
            "horizon_months": horizon_months,
            "mode": mode,
            "sample_period": sample_period,
        }

        if mode == "backtest" and actual_index is not None:
            actual_change_pct = (float(actual_index) / current_index - 1) * 100
            result["actual_index"] = float(actual_index)
            result["actual_change_pct"] = float(actual_change_pct)
            result["delta_abs"] = float(predicted_index - float(actual_index))
            result["delta_pct"] = float(predicted_change_pct - actual_change_pct)

        return result

# Singleton instance
predictor = Predictor()
