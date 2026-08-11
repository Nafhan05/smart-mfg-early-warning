# Laporan Progress - Tahap Data
## Sistem Peringatan Dini Biaya Bahan Baku Manufaktur
### COMPFEST 18 — AI Innovation Challenge

**Tanggal:** 24 Juli 2026
**Branch:** `feature/data`

---

## 1. Ringkasan Pekerjaan

Tahap awal pengumpulan dan pemrosesan data telah selesai. Berikut data yang berhasil dikumpulkan:

### Data yang Tersedia

| Data | Sumber | Periode | Jumlah | Status |
|---|---|---|---|---|
| **Kurs USD/IDR** | Yahoo Finance | 2010-01 s/d 2026-07 | 199 baris | ✅ Siap pakai |
| **IHPB Nasional** | BPS (TABEL8_2.xls) | 2003-01 s/d 2025-09 | 186 baris | ✅ Siap pakai |
| **IHPB Impor** | BPS (TABEL8_2.xls) | 2003-01 s/d 2025-12 | 270 baris | ✅ Siap pakai |

### Data Gabungan (untuk Training)

| File | Lokasi | Baris | Kolom |
|---|---|---|---|
| `data_gabungan_final.csv` | `data/raw/` | 283 | 12 |

---

## 2. Detail Data

### 2.1 Kurs USD/IDR

- **Sumber:** Yahoo Finance (ticker: USDIDR=X)
- **Metode:** Download via `yfinance` library
- **Format:** Bulanan (YYYY-MM)
- **Kolom:** periode, kurs_tengah, kurs_jual, kurs_beli

### 2.2 IHPB (Indeks Harga Perdagangan Besar)

- **Sumber:** BPS via file TABEL8_2.xls
- **Tahun Dasar:** 2018=100 (sudah dinormalisasi)
- **Sektor tersedia:** Pertanian, Pertambangan, Industri, Impor, Ekspor, IHPB Nasional
- **Target:** IHPB Nasional (untuk prediksi)

### 2.3 IHPB Impor

- **Sumber:** BPS (sheet yang sama)
- **Korelasi dengan IHPB Nasional:** 0.849 (sangat kuat)
- **Manfaat:** Fitur prediktor utama

---

## 3. File di Repository

```
data/
├── raw/
│   ├── kurs_usd_idr.csv                    # Data kurs dari Yahoo Finance
│   ├── ihpb_all_sectors_1990_2026.csv      # IHPB semua sektor (mentah)
│   ├── ihpb_all_sectors_normalized.csv     # IHPB semua sektor (normalisasi)
│   ├── ihpb_nasional_normalized.csv        # IHPB Nasional saja
│   ├── ihpb_impor_normalized.csv           # IHPB Impor saja
│   └── data_gabungan_final.csv             # Data gabungan siap training
└── processed/
    └── (akan diisi setelah data cleaning)

dump/
├── scripts/
│   ├── download_kurs_yfinance.py   # Script download kurs
│   ├── extract_ihpb_all_sheets.py  # Script ekstrak IHPB dari BPS
│   ├── merge_final.py              # Script gabungkan semua data
│   ├── auto_download.py            # Script utama (gabungan)
│   └── analyze_data.py             # Script analisis data
└── data/
    └── raw/
        └── (file mentah dari BPS)
```

---

## 4. Temuan Penting

### 4.1 WebAPI BPS

- **Status:** Tidak tersedia untuk data detail
- **Keterangan:** WebAPI hanya mengembalikan metadata (subject, variable), bukan data
- **Solusi:** Download langsung dari portal BPS

### 4.2 Format Data BPS

- File Excel dari BPS memiliki format kompleks
- Perlu parsing khusus untuk mengekstrak data
- Tahun dasar berbeda per periode (2005=100, 2010=100, 2018=100)

### 4.3 Korelasi Data

| Hubungan | Korelasi | Interpretasi |
|---|---|---|
| IHPB Impor → IHPB Nasional | 0.849 | Sangat kuat |
| Kurs → IHPB | -0.452 | Sedang (negatif) |

---

## 5. Yang Perlu Dilanjutkan

### 5.1 P1 (Data & Riset)

- [ ] Validasi data dengan sumber BPS resmi
- [ ] Cek anomali (IHPB = 0)
- [ ] Eksplorasi data harga komoditas global (opsional)

### 5.2 P2 (ML Engineer)

- [ ] Mulai eksplorasi model baseline
- [ ] Feature engineering tambahan
- [ ] Train-test split

### 5.3 P3 (Backend Engineer)

- [ ] Setup struktur backend
- [ ] Implementasi FastAPI skeleton

### 5.4 P4 (Frontend)

- [ ] Mulai desain UI
- [ ] Wireframe flow prediksi

---

## 6. Cara Pakai Data

### Load Data di Python

```python
import pandas as pd

# Load data gabungan
df = pd.read_csv("data/raw/data_gabungan_final.csv")

# Filter data tanpa missing values
df_clean = df.dropna()

# Pisahkan fitur dan target
X = df_clean[["kurs_tengah", "ihpb_impor", "bulan"]]
y = df_clean["ihpb"]
```

### Kolom yang Tersedia

| Kolom | Keterangan | Tipe |
|---|---|---|
| `periode` | Bulan-tahun (YYYY-MM) | string |
| `ihpb` | IHPB Nasional (target utama) | float |
| `kurs_tengah` | Kurs tengah USD/IDR | float |
| `ihpb_impor` | IHPB Impor | float |
| `target_ihpb_h1` | IHPB 1 bulan ke depan | float |
| `target_ihpb_h2` | IHPB 2 bulan ke depan | float |
| `target_ihpb_h3` | IHPB 3 bulan ke depan | float |

---

**Catatan:** Data di folder `dump/` tidak di-push ke GitHub (ada di .gitignore). Script dan data mentah BPS ada di sana untuk referensi.
