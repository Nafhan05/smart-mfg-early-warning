import os
from dotenv import load_dotenv

load_dotenv()

# Cek apakah OpenAI API Key tersedia
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        client = None
        print("Warning: openai library not installed. Using fallback agent.")
else:
    client = None
    print("Warning: OPENAI_API_KEY not found in .env. Using fallback agent.")


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
        "ihpb_impor_pct_change": "Persentase perubahan IHPB Impor"
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
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Anda adalah analis AI yang menghasilkan output JSON valid."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={ "type": "json_object" }
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                "key_drivers": result.get("key_drivers", human_features),
                "recommendation": result.get("recommendation", "Pertimbangkan manajemen stok yang lebih berhati-hati.")
            }
        except Exception as e:
            print(f"LLM API Error: {e}")
            # Fall through to deterministic below
    
    # --- FALLBACK DETERMINISTIC (Bila tidak ada API key atau error) ---
    drivers = [
        f"Pergerakan ini sangat dipengaruhi oleh tren pada {human_features[0].lower()}.",
        f"Selain itu, {human_features[1].lower()} juga menjadi faktor pendorong utama."
    ]
    
    if direction == "naik":
        rec = f"Pertimbangkan untuk mempercepat pembelian stok bahan baku guna mengunci harga saat ini sebelum diproyeksikan naik dalam {horizon} bulan ke depan."
    elif direction == "turun":
        rec = f"Disarankan untuk menunda pembelian besar-besaran karena tren biaya bahan baku diperkirakan menurun dalam {horizon} bulan ke depan."
    else:
        rec = "Pertahankan tingkat persediaan normal, karena tidak ada proyeksi gejolak harga yang signifikan dalam waktu dekat."
        
    return {
        "key_drivers": drivers,
        "recommendation": rec
    }
