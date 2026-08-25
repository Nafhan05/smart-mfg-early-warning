import pandas as pd
import numpy as np
import joblib
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
        model_path = Path(__file__).parent.parent / "model" / "model.pkl"
        if model_path.exists():
            self.models = joblib.load(model_path)
            print("Models loaded successfully.")
        else:
            print(f"Warning: Model not found at {model_path}. Please run train.py first.")
            self.models = None
            
    def load_data(self):
        data_path = Path(__file__).parent.parent / "data" / "processed" / "dataset_ready.csv"
        if data_path.exists():
            return pd.read_csv(data_path)
        else:
            print(f"Warning: Data not found at {data_path}.")
            return None

    def predict(self, sector: str, horizon_months: int):
        """
        Lakukan prediksi untuk sektor tertentu sejauh horizon_months ke depan.
        Saat ini menggunakan data baris terakhir (terbaru) sebagai base.
        """
        if self.models is None or self.dataset_ready is None:
            raise RuntimeError("Model or Data not loaded.")
            
        model_key = f"horizon_{horizon_months}"
        if model_key not in self.models:
            raise ValueError(f"Model for horizon {horizon_months} not available.")
            
        model_data = self.models[model_key]
        model = model_data['model']
        features = model_data['features']
        
        # Ambil row terakhir dari dataset untuk inference
        # (Idealnya dalam sistem production sungguhan, 
        # input fitur diberikan dari database secara live)
        df_latest = self.dataset_ready.tail(1).copy()
        
        # Buat feature matrix menggunakan fungsi dari model/features.py
        df_feat = build_feature_matrix(self.dataset_ready)
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
            
        return {
            "current_index": float(current_index),
            "predicted_index": float(predicted_index),
            "predicted_change_pct": float(predicted_change_pct),
            "direction": direction,
            "top_features": top_features,
            "horizon_months": horizon_months
        }

# Singleton instance
predictor = Predictor()
