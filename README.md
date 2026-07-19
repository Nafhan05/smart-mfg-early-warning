# Smart Manufacturing Early Warning

Sistem Peringatan Dini Biaya Bahan Baku Manufaktur untuk COMPFEST 18 — AI Innovation Challenge (Pilar: Smart Manufacturing).

## Ringkasan

Sistem ini meramal pergerakan **Indeks Harga Perdagangan Besar (IHPB) Bahan Baku** untuk sektor Makanan-Minuman, 1-3 bulan ke depan, lalu menjelaskan faktor pendorongnya dan memberi rekomendasi aksi ke pengguna.

## Komponen

1. **Model Prediktif** — Gradient boosting (LightGBM) yang dilatih dari data historis BPS
2. **Agent Penjelas** — LLM yang menerjemahkan output model menjadi penjelasan dan rekomendasi
3. **Backend API** — FastAPI endpoint untuk inferensi
4. **Frontend** — Single-page app untuk interaksi pengguna

## Prasyarat

- Docker & Docker Compose
- API key untuk LLM (OpenAI atau Anthropic) — opsional untuk MVP

## Instalasi & Menjalankan

```bash
# 1. Clone repository
git clone https://github.com/[username]/smart-mfg-early-warning.git
cd smart-mfg-early-warning

# 2. Buat file .env dari template
cp .env.example .env

# 3. Edit .env dan masukkan API key (jika menggunakan LLM agent)
# nano .env

# 4. Jalankan seluruh sistem
docker compose up

# 5. Akses aplikasi
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Struktur Folder

```
smart-mfg-early-warning/
├── README.md                 # Dokumen ini
├── docker-compose.yml        # Konfigurasi Docker
├── .env.example              # Template environment variables
├── data/
│   ├── raw/                  # Data mentah BPS, IHPB, Kurs
│   ├── processed/            # Data bersih siap training
│   └── README.md             # Sumber & cara peroleh data
├── notebooks/                # EDA, tidak di-deploy
├── model/
│   ├── train.py              # Script training (jalan manual sekali)
│   ├── features.py           # Feature engineering
│   └── evaluate.py           # Backtesting & evaluasi
├── backend/
│   ├── main.py               # Entry point FastAPI
│   ├── predictor.py          # Load model, fungsi predict()
│   ├── agent.py              # Logic panggil LLM
│   ├── schemas.py            # Request/response Pydantic
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Container backend
├── frontend/
│   ├── index.html            # Single page app
│   ├── style.css             # Styling
│   └── app.js                # Logic frontend
└── docs/
    └── architecture.md       # Diagram arsitektur
```

## API Endpoints

- `GET /health` — Health check
- `POST /predict` — Prediksi pergerakan IHPB

Contoh request:
```json
{
  "sector": "makanan-minuman",
  "horizon_months": 2
}
```

## Model

Model sudah pre-trained dan tersimpan di `model/model.pkl`. Untuk re-training:

```bash
cd model
python train.py
```

## Catatan Teknis

- Data historis diambil dari BPS (Ekspor-Impor, IHPB) dan Bank Indonesia (Kurs)
- Model menggunakan gradient boosting untuk prediksi time-series tabular
- Agent menggunakan LLM API untuk menghasilkan penjelasan dan rekomendasi
- Seluruh sistem bisa dijalankan dengan satu perintah `docker compose up`

## Lisensi

Project ini dibuat untuk COMPFEST 18 — AI Innovation Challenge.
