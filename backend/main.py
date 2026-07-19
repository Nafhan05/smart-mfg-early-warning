"""
Backend FastAPI untuk Sistem Peringatan Dini Biaya Bahan Baku.
Endpoint utama: POST /predict
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import PredictRequest, PredictResponse

app = FastAPI(
    title="Smart Manufacturing Early Warning API",
    description="API untuk prediksi pergerakan IHPB Bahan Baku",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "smart-mfg-early-warning"}


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Prediksi pergerakan IHPB Bahan Baku.
    
    - sector: Sektor manufaktur (saat ini hanya "makanan-minuman")
    - horizon_months: Berapa bulan ke depan (1-3)
    """
    # TODO: Implementasi oleh P3 (Backend Engineer)
    # 1. Load model dari model/model.pkl
    # 2. Proses fitur input
    # 3. Jalankan prediksi
    # 4. Panggil agent untuk penjelasan
    # 5. Kembalikan response
    
    # Placeholder response untuk testing
    return PredictResponse(
        sector=request.sector,
        horizon_months=request.horizon_months,
        current_index=100.0,
        predicted_index=105.0,
        predicted_change_pct=5.0,
        direction="naik",
        key_drivers=[
            "Pelemahan rupiah terhadap dolar AS",
            "Kenaikan harga gula global"
        ],
        recommendation="Pertimbangkan pembelian stok bahan baku dalam waktu dekat atau eksplorasi alternatif bahan lokal untuk mengurangi eksposur terhadap kenaikan harga."
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
