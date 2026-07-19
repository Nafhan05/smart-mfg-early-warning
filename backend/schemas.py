"""
Pydantic models untuk request/response API.
"""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class Sector(str, Enum):
    """Sektor manufaktur yang didukung."""
    MAKANAN_MINUMAN = "makanan-minuman"


class Direction(str, Enum):
    """Arah pergerakan indeks."""
    NAIK = "naik"
    TURUN = "turun"
    STABIL = "stabil"


class PredictRequest(BaseModel):
    """Request body untuk endpoint /predict."""
    sector: Sector = Field(
        ...,
        description="Sektor manufaktur yang ingin diprediksi",
        example="makanan-minuman"
    )
    horizon_months: int = Field(
        ...,
        ge=1,
        le=3,
        description="Berapa bulan ke depan yang ingin diprediksi (1-3)",
        example=2
    )


class PredictResponse(BaseModel):
    """Response body untuk endpoint /predict."""
    sector: str = Field(..., description="Sektor yang diramal")
    horizon_months: int = Field(..., description="Berapa bulan ke depan diramal")
    current_index: float = Field(..., description="Nilai IHPB terkini (baseline)")
    predicted_index: float = Field(..., description="Nilai IHPB hasil prediksi model")
    predicted_change_pct: float = Field(..., description="Perubahan % dari current ke predicted")
    direction: Direction = Field(..., description="Arah pergerakan: naik/turun/stabil")
    key_drivers: List[str] = Field(..., description="Daftar faktor pendorong utama")
    recommendation: str = Field(..., description="Rekomendasi aksi dari agent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sector": "makanan-minuman",
                "horizon_months": 2,
                "current_index": 118.4,
                "predicted_index": 126.9,
                "predicted_change_pct": 7.2,
                "direction": "naik",
                "key_drivers": [
                    "Pelemahan rupiah terhadap dolar AS",
                    "Penurunan volume impor gula dari negara asal utama"
                ],
                "recommendation": "Pertimbangkan pembelian stok gula dalam waktu dekat atau eksplorasi alternatif bahan lokal untuk mengurangi eksposur terhadap kenaikan harga."
            }
        }
