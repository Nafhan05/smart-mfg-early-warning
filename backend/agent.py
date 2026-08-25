import os
import json
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Multi-provider LLM
# ------------------------------------------------------------
# Semua provider di bawah menyediakan endpoint OpenAI-compatible,
# sehingga cukup memakai OpenAI SDK dengan base_url yang berbeda.
#
# Konfigurasi via environment variable (opsional):
#   LLM_PROVIDER  : openai | gemini | deepseek | openrouter | custom
#   LLM_API_KEY   : API key provider (fallback ke OPENAI_API_KEY)
#   LLM_MODEL     : nama model (jika kosong, pakai default provider)
#   LLM_BASE_URL  : base URL custom (untuk provider = custom)
#   LLM_JSON_MODE : "true"/"false" — aktifkan response_format json
#
# Tanpa API key sama sekali, agent memakai fallback deterministic.
# ============================================================

LLM_PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
        "json_mode": True,
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.0-flash",
        "json_mode": False,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "json_mode": True,
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-4o-mini",
        "json_mode": False,
    },
}


def _resolve_llm_config():
    """Resolve provider, API key, model, dan base URL dari env."""
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    config = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["openai"])

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL") or config["model"]
    base_url = os.getenv("LLM_BASE_URL") or config["base_url"]
    json_mode = os.getenv("LLM_JSON_MODE", str(config["json_mode"])).lower() in (
        "1", "true", "yes"
    )
    return provider, api_key, model, base_url, json_mode


provider, llm_api_key, llm_model, llm_base_url, llm_json_mode = _resolve_llm_config()

client = None
if llm_api_key:
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=llm_api_key, base_url=llm_base_url)
        print(f"LLM provider: {provider} (model: {llm_model})")
    except ImportError:
        client = None
        print("Warning: openai library not installed. Using fallback agent.")
else:
    print("Warning: LLM API key tidak ditemukan. Menggunakan fallback agent.")


def get_feature_name_human_readable(feature: str) -> str:
    """Ubah nama kolom menjadi bahasa manusia."""
    mapping = {
        "ihpb_impor": "Indeks harga impor",
        "ihpb_impor_lag_1": "Indeks harga impor bulan lalu",
        "kurs_tengah": "Kurs Rupiah terhadap USD",
        "kurs_tengah_lag_1": "Kurs Rupiah terhadap USD bulan lalu",
        "ihpb_industri": "Indeks harga industri",
        "ihpb_nasional_lag_1": "Tren IHPB Nasional bulan sebelumnya",
        "bulan_sin": "Pola musiman tahunan",
        "bulan_cos": "Pola musiman tahunan",
        "is_nataru": "Mendekati periode Lebaran/Nataru",
        "kurs_tengah_pct_change": "Persentase perubahan kurs Rupiah",
        "ihpb_impor_pct_change": "Persentase perubahan IHPB Impor",
    }

    # Cek yang mirip
    for key, val in mapping.items():
        if key in feature:
            return val

    return feature.replace("_", " ").title()


async def generate_explanation(prediction_data: dict) -> dict:
    """
    Panggil LLM untuk menghasilkan penjelasan (key_drivers) dan rekomendasi.
    Fallback ke deterministic string jika API key tidak tersedia.
    """
    direction = prediction_data["direction"]
    horizon = prediction_data["horizon_months"]
    top_features = prediction_data["top_features"]

    human_features = [get_feature_name_human_readable(f) for f in top_features]

    if client:
        try:
            prompt = f"""
            Anda adalah analis ekonomi industri manufaktur.
            Sistem prediksi AI kami baru saja memprediksi bahwa Indeks Harga Perdagangan Besar (IHPB) bahan baku 
            untuk sektor Makanan dan Minuman akan mengalami pergerakan: {direction.upper()} 
            dalam {horizon} bulan ke depan.
            
            Faktor-faktor utama yang mendorong pergerakan ini berdasarkan model prediktif kami adalah:
            1. {human_features[0]}
            2. {human_features[1]}
            3. {human_features[2]}
            
            Berdasarkan data di atas, berikan:
            1. Dua kalimat penjelasan yang profesional namun mudah dipahami (key drivers).
            2. Satu kalimat rekomendasi aksi bisnis yang konkret (misal: soal manajemen stok/pembelian) untuk perusahaan manufaktur.
            
            Format balasan Anda HARUS dalam JSON seperti ini, tanpa markdown lain:
            {{
                "key_drivers": ["penjelasan 1", "penjelasan 2"],
                "recommendation": "rekomendasi aksi"
            }}
            """

            kwargs = {
                "model": llm_model,
                "messages": [
                    {"role": "system", "content": "Anda adalah analis AI yang menghasilkan output JSON valid."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
            }
            if llm_json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = await client.chat.completions.create(**kwargs)
            result = json.loads(response.choices[0].message.content)
            return {
                "key_drivers": result.get("key_drivers", human_features),
                "recommendation": result.get(
                    "recommendation", "Pertimbangkan manajemen stok yang lebih berhati-hati."
                ),
            }
        except Exception as e:
            print(f"LLM API Error: {e}")
            # Fall through to deterministic below

    # --- FALLBACK DETERMINISTIC (Bila tidak ada API key atau error) ---
    drivers = [
        f"Pergerakan ini sangat dipengaruhi oleh tren pada {human_features[0].lower()}.",
        f"Selain itu, {human_features[1].lower()} juga menjadi faktor pendorong utama.",
    ]

    if direction == "naik":
        rec = f"Pertimbangkan untuk mempercepat pembelian stok bahan baku guna mengunci harga saat ini sebelum diproyeksikan naik dalam {horizon} bulan ke depan."
    elif direction == "turun":
        rec = f"Disarankan untuk menunda pembelian besar-besaran karena tren biaya bahan baku diperkirakan menurun dalam {horizon} bulan ke depan."
    else:
        rec = "Pertahankan tingkat persediaan normal, karena tidak ada proyeksi gejolak harga yang signifikan dalam waktu dekat."

    return {
        "key_drivers": drivers,
        "recommendation": rec,
    }