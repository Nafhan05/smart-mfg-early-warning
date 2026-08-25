"""
Script evaluasi & backtesting model prediktif IHPB.
Metrik: MAE, RMSE, directional accuracy.
Output: grafik prediksi vs aktual + tabel metrik, disimpan di model/evaluation/
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from features import build_feature_matrix


# ══════════════════════════════════════════════════════════════
# FUNGSI EVALUASI
# ══════════════════════════════════════════════════════════════

def directional_accuracy(y_true, y_pred, y_baseline):
    """Hitung seberapa sering arah naik/turun diprediksi benar."""
    actual_dir = np.sign(y_true - y_baseline)
    pred_dir = np.sign(y_pred - y_baseline)
    # Kalau tidak berubah, anggap "naik" (positif)
    actual_dir = np.where(actual_dir == 0, 1, actual_dir)
    pred_dir = np.where(pred_dir == 0, 1, pred_dir)
    return (actual_dir == pred_dir).sum() / len(y_true)


def evaluate_predictions(y_true, y_pred, y_baseline):
    """Hitung semua metrik evaluasi."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    dir_acc = directional_accuracy(y_true, y_pred, y_baseline)
    
    # Naive baseline: prediksi = nilai saat ini (no change)
    naive_mae = mean_absolute_error(y_true, y_baseline)
    naive_rmse = root_mean_squared_error(y_true, y_baseline)
    
    return {
        'mae': mae,
        'rmse': rmse,
        'dir_acc': dir_acc,
        'naive_mae': naive_mae,
        'naive_rmse': naive_rmse,
        'mae_improvement': ((naive_mae - mae) / naive_mae) * 100 if naive_mae > 0 else 0
    }


# ══════════════════════════════════════════════════════════════
# GRAFIK
# ══════════════════════════════════════════════════════════════

def plot_predictions_vs_actual(periods, y_true, y_pred, y_baseline, horizon, metrics, save_path):
    """Grafik prediksi vs aktual untuk satu horizon."""
    fig, ax = plt.subplots(figsize=(12, 5))
    
    x = range(len(periods))
    ax.plot(x, y_true, 'o-', color='#2563EB', label='Aktual', linewidth=2, markersize=6)
    ax.plot(x, y_pred, 's--', color='#DC2626', label='Prediksi Model', linewidth=2, markersize=6)
    ax.plot(x, y_baseline, '^:', color='#9CA3AF', label='Baseline (Naif)', linewidth=1.5, markersize=5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(periods, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('IHPB Nasional', fontsize=11)
    ax.set_title(f'Prediksi vs Aktual — Horizon {horizon} Bulan', fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Teks metrik di grafik
    textstr = f"MAE: {metrics['mae']:.3f}  |  RMSE: {metrics['rmse']:.3f}  |  Dir.Acc: {metrics['dir_acc']*100:.1f}%"
    ax.text(0.5, -0.22, textstr, transform=ax.transAxes, fontsize=10,
            ha='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#F0F9FF', edgecolor='#93C5FD'))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


def plot_feature_importance(model, feature_names, horizon, save_path, top_n=15):
    """Grafik feature importance dari LightGBM."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[-top_n:]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(indices)))
    ax.barh(range(len(indices)), importances[indices], color=colors)
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices], fontsize=9)
    ax.set_xlabel('Importance (split count)', fontsize=11)
    ax.set_title(f'Top {top_n} Feature Importance — Horizon {horizon} Bulan', fontsize=13, fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


def plot_metrics_comparison(all_metrics, save_path):
    """Grafik perbandingan metrik antar horizon."""
    horizons = list(all_metrics.keys())
    mae_model = [all_metrics[h]['mae'] for h in horizons]
    mae_naive = [all_metrics[h]['naive_mae'] for h in horizons]
    rmse_model = [all_metrics[h]['rmse'] for h in horizons]
    rmse_naive = [all_metrics[h]['naive_rmse'] for h in horizons]
    dir_accs = [all_metrics[h]['dir_acc'] * 100 for h in horizons]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    x = np.arange(len(horizons))
    w = 0.35
    
    # MAE
    axes[0].bar(x - w/2, mae_naive, w, label='Baseline Naif', color='#D1D5DB')
    axes[0].bar(x + w/2, mae_model, w, label='Model LightGBM', color='#3B82F6')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f'H{h}' for h in horizons])
    axes[0].set_ylabel('MAE')
    axes[0].set_title('MAE: Model vs Baseline', fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, axis='y', alpha=0.3)
    
    # RMSE
    axes[1].bar(x - w/2, rmse_naive, w, label='Baseline Naif', color='#D1D5DB')
    axes[1].bar(x + w/2, rmse_model, w, label='Model LightGBM', color='#EF4444')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([f'H{h}' for h in horizons])
    axes[1].set_ylabel('RMSE')
    axes[1].set_title('RMSE: Model vs Baseline', fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, axis='y', alpha=0.3)
    
    # Directional Accuracy
    bars = axes[2].bar(x, dir_accs, color=['#10B981', '#F59E0B', '#EF4444'])
    axes[2].axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='Random (50%)')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels([f'H{h}' for h in horizons])
    axes[2].set_ylabel('Directional Accuracy (%)')
    axes[2].set_title('Directional Accuracy', fontweight='bold')
    axes[2].set_ylim(0, 100)
    axes[2].legend()
    axes[2].grid(True, axis='y', alpha=0.3)
    for bar, val in zip(bars, dir_accs):
        axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                     f'{val:.1f}%', ha='center', fontweight='bold')
    
    plt.suptitle('Perbandingan Metrik Model LightGBM', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    """Jalankan evaluasi lengkap pada model yang sudah di-training."""
    print("=" * 60)
    print("MODEL EVALUATION & BACKTESTING")
    print("Smart Manufacturing Early Warning")
    print("=" * 60)
    
    # Setup output directory
    eval_dir = Path(__file__).parent / "evaluation"
    eval_dir.mkdir(exist_ok=True)
    
    # Load model
    model_path = Path(__file__).parent / "model.pkl"
    if not model_path.exists():
        print("ERROR: model.pkl not found. Run train.py first.")
        return
    
    models = joblib.load(model_path)
    print(f"Loaded models: {list(models.keys())}")
    
    # Load & prepare data
    data_path = Path(__file__).parent.parent / "data" / "processed" / "dataset_ready.csv"
    df = pd.read_csv(data_path)
    df_feat = build_feature_matrix(df)
    
    test_size = 12  # Sama dengan saat training
    
    # Exclude non-feature columns
    exclude_cols = ['periode', 'year', 'target_ihpb_h1', 'target_change_pct_h1', 'target_direction_h1',
                    'target_ihpb_h2', 'target_change_pct_h2', 'target_direction_h2',
                    'target_ihpb_h3', 'target_change_pct_h3', 'target_direction_h3']
    feature_cols = [c for c in df_feat.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_feat[c])]
    
    all_metrics = {}
    
    for h in [1, 2, 3]:
        print(f"\n{'─' * 40}")
        print(f"  HORIZON {h} BULAN")
        print(f"{'─' * 40}")
        
        target_col = f'target_ihpb_h{h}'
        df_clean = df_feat.dropna(subset=[target_col]).copy()
        
        test_df = df_clean.iloc[-test_size:]
        
        model_data = models[f'horizon_{h}']
        model = model_data['model']
        features = model_data['features']
        
        X_test = test_df[features]
        y_true = test_df[target_col].values
        y_baseline = test_df['ihpb_nasional'].values
        periods = test_df['periode'].values
        
        # Model memprediksi pct_change, konversi ke absolut
        y_pred_pct = model.predict(X_test)
        y_pred = y_baseline * (1 + y_pred_pct / 100)
        
        # Hitung metrik
        metrics = evaluate_predictions(y_true, y_pred, y_baseline)
        all_metrics[h] = metrics
        
        print(f"  MAE          : {metrics['mae']:.4f} (baseline naif: {metrics['naive_mae']:.4f})")
        print(f"  RMSE         : {metrics['rmse']:.4f} (baseline naif: {metrics['naive_rmse']:.4f})")
        print(f"  Dir. Accuracy: {metrics['dir_acc']*100:.1f}%")
        print(f"  MAE Improvement vs Naive: {metrics['mae_improvement']:.1f}%")
        
        # Grafik prediksi vs aktual
        plot_predictions_vs_actual(
            periods, y_true, y_pred, y_baseline, h, metrics,
            eval_dir / f"pred_vs_actual_h{h}.png"
        )
        
        # Grafik feature importance
        plot_feature_importance(
            model, features, h,
            eval_dir / f"feature_importance_h{h}.png"
        )
    
    # Grafik perbandingan metrik antar horizon
    print(f"\n{'─' * 40}")
    print("  SUMMARY")
    print(f"{'─' * 40}")
    plot_metrics_comparison(all_metrics, eval_dir / "metrics_comparison.png")
    
    # Simpan tabel ringkasan ke file teks
    summary_path = eval_dir / "evaluation_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("MODEL EVALUATION SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"{'Horizon':<10} {'MAE':<10} {'RMSE':<10} {'DirAcc':<10} {'Naive MAE':<12} {'Improvement':<12}\n")
        f.write("-" * 64 + "\n")
        for h, m in all_metrics.items():
            f.write(f"{h} bulan    {m['mae']:<10.4f} {m['rmse']:<10.4f} {m['dir_acc']*100:<10.1f} {m['naive_mae']:<12.4f} {m['mae_improvement']:<12.1f}%\n")
        
        f.write(f"\nTest period: {test_size} bulan terakhir\n")
        f.write(f"Training split: time-based (bukan random)\n")
        f.write(f"Model: LightGBM (gradient boosting)\n")
    
    print(f"  Saved: {summary_path}")
    
    print(f"\n{'=' * 60}")
    print(f"Semua hasil evaluasi tersimpan di: {eval_dir}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
