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


from predictor import predictor
from agent import generate_explanation

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Prediksi pergerakan IHPB Bahan Baku.
    
    - sector: Sektor manufaktur (saat ini hanya "makanan-minuman")
    - horizon_months: Berapa bulan ke depan (1-3)
    """
    try:
        # 1. Jalankan prediksi dari model LightGBM
        pred_result = predictor.predict(request.sector, request.horizon_months)
        
        # 2. Panggil agent untuk penjelasan (LLM / Fallback)
        agent_result = await generate_explanation(pred_result)
        
        # 3. Kembalikan response gabungan
        return PredictResponse(
            sector=request.sector,
            horizon_months=request.horizon_months,
            current_index=pred_result["current_index"],
            predicted_index=pred_result["predicted_index"],
            predicted_change_pct=pred_result["predicted_change_pct"],
            direction=pred_result["direction"],
            key_drivers=agent_result["key_drivers"],
            recommendation=agent_result["recommendation"]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback response for safe error handling during demo
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
