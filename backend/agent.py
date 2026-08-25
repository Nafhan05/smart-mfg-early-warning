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


import re

def get_feature_name_human_readable(feature: str) -> str:
    """Ubah nama kolom menjadi bahasa manusia dengan rapi."""
    
    # Mapping dasar untuk prefix utama
    base_mapping = {
        "ihpb_nasional": "IHPB Nasional",
        "ihpb_industri": "IHPB Sektor Industri",
        "ihpb_impor": "IHPB Impor Bahan Baku",
        "kurs_tengah": "Kurs Rupiah terhadap USD",
"is_nataru": "Periode mendekati Lebaran/Nataru",
        "bulan_sin": "Pola musiman siklikal (Sinus)",
        "bulan_cos": "Pola musiman siklikal (Cosinus)"
    }
    
    human_name = feature
    for base, name in base_mapping.items():
        if feature.startswith(base):
            human_name = name
            break
            
    if human_name == feature:
        human_name = feature.replace("_", " ").title()
        
    # Tambahkan penjelasan suffix jika ada
    if "_lag_" in feature:
        lag_num = re.search(r'_lag_(\d+)', feature)
        if lag_num:
            human_name += f" ({lag_num.group(1)} bulan sebelumnya)"
            
    if "_rolling_mean_" in feature:
        win_num = re.search(r'_rolling_mean_(\d+)', feature)
        if win_num:
            human_name += f" (Rata-rata pergerakan {win_num.group(1)} bulan terakhir)"
            
    if "_rolling_std_" in feature:
        win_num = re.search(r'_rolling_std_(\d+)', feature)
        if win_num:
            human_name += f" (Volatilitas {win_num.group(1)} bulan terakhir)"
            
    if "_pct_change" in feature:
        human_name += " (Persentase perubahan)"
        
    return human_name


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