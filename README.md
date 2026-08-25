# Smart Manufacturing Early Warning

Sistem peringatan dini biaya bahan baku manufaktur — meramal pergerakan **Indeks Harga Perdagangan Besar (IHPB) Bahan Baku** untuk sektor makanan & minuman 1–3 bulan ke depan, lalu menjelaskan faktor pendorong dan memberikan rekomendasi aksi.

Dibuat untuk **COMPFEST 18 — AI Innovation Challenge** (Pilar: Smart Manufacturing).

---

## Cara Kerja

Pengguna memilih horizon prediksi (1, 2, atau 3 bulan) lalu menekan tombol "Jalankan prediksi". Sistem menampilkan:

- Proyeksi nilai IHPB dan perubahan %
- Arah pergerakan (naik / turun / stabil)
- Faktor pendorong utama
- Rekomendasi aksi bisnis

## Komponen

| Komponen | Teknologi | Peran |
|---|---|---|
| Model prediktif | Python + LightGBM | Memprediksi perubahan IHPB dari fitur historis |
| Agent penjelas | Python (OpenAI, opsional) | Menerjemahkan output model jadi narasi & rekomendasi |
| Backend API | FastAPI | Satu endpoint `POST /predict` |
| Frontend | HTML + CSS + JS | Satu halaman input → hasil |
| Infrastruktur | Docker Compose | Menjalankan seluruh sistem dengan satu perintah |

## Prasyarat

- Docker & Docker Compose (versi terbaru)
- API key OpenAI — **opsional**. Tanpa API key, agent memakai fallback deterministic sehingga sistem tetap berfungsi penuh.

## Menjalankan

```bash
# 1. Clone repository
git clone https://github.com/Nafhan05/smart-mfg-early-warning.git
cd smart-mfg-early-warning

# 2. (Opsional) Sediakan API key untuk agent LLM
#    Salin .env.example menjadi .env lalu isi OPENAI_API_KEY.
#    Tanpa langkah ini sistem tetap berjalan memakai fallback.

# 3. Jalankan seluruh sistem
docker compose up --build

# 4. Akses
#    Frontend : http://localhost:3000
#    Backend  : http://localhost:8000
#    API docs : http://localhost:8000/docs
```

## Struktur Folder

```
smart-mfg-early-warning/
├── README.md
├── docker-compose.yml          # Orkestrasi backend + frontend
├── .env.example                # Template variabel lingkungan (opsional)
├── backend/
│   ├── main.py                 # Entry point FastAPI (endpoint /health & /predict)
│   ├── predictor.py            # Memuat model & dataset, fungsi predict()
│   ├── agent.py                # Penjelasan & rekomendasi (LLM + fallback)
│   ├── schemas.py              # Skema request/response Pydantic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html              # Satu halaman aplikasi
│   ├── style.css
│   └── app.js                  # Pemanggil API /predict
├── model/
│   ├── train.py                # Script training LightGBM
│   ├── features.py             # Feature engineering (dipakai saat inference)
│   ├── evaluate.py             # Backtesting & evaluasi
│   ├── model.pkl               # Model pre-trained
│   └── evaluation/             # Grafik & ringkasan hasil evaluasi
├── data/
│   ├── process.py              # Pipeline data mentah → siap training
│   ├── raw/                    # Data mentah (kurs, IHPB, impor)
│   ├── processed/              # Dataset siap training + ringkasan
│   └── README.md               # Sumber & cara memperoleh data
└── notebooks/                  # Eksplorasi data (tidak di-deploy)
```

## API

### `GET /health`

Mengecek status layanan.

### `POST /predict`

Contoh request:

```json
{
  "sector": "makanan-minuman",
  "horizon_months": 2
}
```

Contoh response:

```json
{
  "sector": "makanan-minuman",
  "horizon_months": 2,
  "current_index": 156.3,
  "predicted_index": 155.9,
  "predicted_change_pct": -0.26,
  "direction": "stabil",
  "key_drivers": [
    "Pergerakan ini sangat dipengaruhi oleh tren pada kurs rupiah terhadap usd.",
    "Selain itu, indeks harga industri juga menjadi faktor pendorong utama."
  ],
  "recommendation": "Pertahankan tingkat persediaan normal, karena tidak ada proyeksi gejolak harga yang signifikan dalam waktu dekat."
}
```

| Field | Keterangan |
|---|---|
| `direction` | `naik`, `turun`, atau `stabil` |
| `key_drivers` | Faktor pendorong utama dari feature importance model |
| `recommendation` | Rekomendasi aksi (stocking, tunda beli, dsb.) |

Dokumentasi interaktif tersedia di `http://localhost:8000/docs`.

## Data

| Data | Sumber | Periode |
|---|---|---|
| Kurs USD/IDR | Yahoo Finance | 2010–2026 |
| IHPB (Nasional, Industri, Impor) | BPS | 2003–2025 |
| Nilai impor per komoditas (HS 17) | BPS | 2014–2025 |

Data mentah disimpan di `data/raw/`, diproses oleh `data/process.py`, dan hasilnya (`dataset_ready.csv`) menjadi input training. Detail sumber ada di `data/README.md`.

## Model

Model sudah **pre-trained** dan tersimpan di `model/model.pkl`. Untuk melatih ulang:

```bash
# 1. Proses data mentah menjadi dataset siap training
python data/process.py

# 2. Latih model
python model/train.py
```

Hasil evaluasi (MAE, RMSE, directional accuracy, grafik prediksi vs aktual) ada di `model/evaluation/`.

## Catatan Teknis

- Prediksi memakai **perubahan %** (pct_change) dari nilai IHPB saat ini — lebih stabil untuk deret waktu pendek.
- Split data berbasis waktu (time-based), bukan acak, untuk menghindari bocornya informasi masa depan.
- Semua variabel (model, dataset) dimuat dari environment variable; tanpa API key, agent menggunakan fallback deterministic.
- Tidak memerlukan database — data disimpan sebagai file lokal.

## Lisensi

Dibuat untuk COMPFEST 18 — AI Innovation Challenge.