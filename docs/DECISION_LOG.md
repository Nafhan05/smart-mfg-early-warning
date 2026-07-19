# Decision Log
## Sistem Peringatan Dini Biaya Bahan Baku Manufaktur — COMPFEST 18 AIC

Dokumen ini mencatat setiap keputusan penting tim beserta alasannya, alternatif yang dipertimbangkan, dan siapa yang memutuskan. Tujuannya dua:
1. Supaya nggak ada perdebatan ulang "kenapa dulu kita pilih ini" di tengah jalan.
2. Mempercepat penulisan proposal — bagian metodologi wajib menjelaskan alasan pengambilan keputusan teknis, jadi tinggal salin dari sini.

**Cara pakai:** setiap kali tim mengambil keputusan yang cukup signifikan (pemilihan teknologi, scope, pendekatan, dsb — bukan hal kecil sehari-hari), tambahkan satu baris baru. Jangan tunggu sampai lupa alasannya.

---

## Log Keputusan

### 001 — Pemilihan ide/masalah utama

| Field | Isi |
|---|---|
| **Tanggal** | *(isi tanggal diskusi tim)* |
| **Keputusan** | Fokus ke Smart Manufacturing: Sistem Peringatan Dini Biaya Bahan Baku, berbasis data BPS Ekspor-Impor dan IHPB Bahan Baku |
| **Alternatif dipertimbangkan** | (1) Skor kepastian pengiriman berbasis data PIHPS untuk Smart Logistics, (2) Radar peluang substitusi impor, (3) Analisis daya saing produk lokal vs impor di marketplace |
| **Alasan** | Data ekspor-impor & IHPB tersedia publik dan resmi (BPS), sektor manufaktur cocok dengan pilar tema, dan setelah dipatch (lihat #002) punya elemen prediktif yang jelas dan ground truth yang terukur |
| **Diputuskan oleh** | *(isi nama/tim)* |
| **Status** | Final |

### 002 — Target variabel model: IHPB Bahan Baku, bukan rasio ketergantungan impor

| Field | Isi |
|---|---|
| **Tanggal** | *(isi tanggal)* |
| **Keputusan** | Model memprediksi nilai Indeks Harga Perdagangan Besar (IHPB) Bahan Baku per sektor, bukan sekadar rasio nilai impor/kebutuhan sektor |
| **Alternatif dipertimbangkan** | Rasio ketergantungan impor sederhana (nilai impor dibagi total kebutuhan sektor) |
| **Alasan** | Rasio ketergantungan itu perhitungan statis, bukan machine learning genuine, dan tidak ada ground truth historis yang jelas untuk validasi. IHPB adalah angka resmi yang dipublikasikan BPS bulanan sejak 2010, sehingga bisa dipakai sebagai label riil untuk training & backtesting |
| **Diputuskan oleh** | *(isi nama/tim)* |
| **Status** | Final |

### 003 — Cakupan sektor: 1-2 sektor, bukan seluruh sektor manufaktur

| Field | Isi |
|---|---|
| **Tanggal** | *(isi tanggal)* |
| **Keputusan** | MVP hanya mencakup 1-2 sektor manufaktur (kandidat: tekstil atau makanan-minuman) |
| **Alternatif dipertimbangkan** | Cover seluruh/banyak sektor sekaligus untuk kelihatan lebih komprehensif |
| **Alasan** | Tiap sektor punya pola & indikator eksogen berbeda (cuaca untuk pertanian, harga logam global untuk sektor mesin, dsb). Dengan waktu ~6 minggu dan tim 4 orang, cakupan luas akan menghasilkan model dangkal di semua sektor. Kriteria penilaian berbobot tertinggi (25%) menilai kematangan arsitektur, bukan cakupan. Roadmap scale-up ke sektor lain dicantumkan di proposal sebagai potensi pengembangan, bukan dieksekusi penuh di tahap penyisihan |
| **Diputuskan oleh** | *(isi nama/tim)* |
| **Status** | Final |

### 004 — Sektor final yang dipilih

| Field | Isi |
|---|---|
| **Tanggal** | *(isi tanggal)* |
| **Keputusan** | *(isi: tekstil / makanan-minuman / lainnya)* |
| **Alternatif dipertimbangkan** | *(isi sektor lain yang sempat dipertimbangkan)* |
| **Alasan** | *(isi: kelengkapan data, relevansi dengan isu bahan baku impor, ketersediaan kode HS yang jelas, dsb)* |
| **Diputuskan oleh** | *(isi nama/tim)* |
| **Status** | ⏳ Belum diputuskan |

### 005 — Pendekatan model prediktif

| Field | Isi |
|---|---|
| **Tanggal** | *(isi tanggal)* |
| **Keputusan** | Gradient boosting (LightGBM/XGBoost) untuk prediksi tabular time-series, bukan deep learning (LSTM/Transformer) |
| **Alternatif dipertimbangkan** | LSTM, model time-series klasik (ARIMA) |
| **Alasan** | Data historis bulanan relatif pendek (puluhan-ratusan baris per sektor), gradient boosting lebih cepat dikembangkan & dievaluasi dalam waktu terbatas, dan lebih mudah diinterpretasi lewat feature importance untuk menjelaskan "faktor pendorong" ke pengguna |
| **Diputuskan oleh** | *(isi nama/tim)* |
| **Status** | Diusulkan — konfirmasi setelah eksperimen awal di Minggu 3 |

### 006 — Pendekatan agent penjelas: prompting vs fine-tuning

| Field | Isi |
|---|---|
| **Tanggal** | *(isi tanggal)* |
| **Keputusan** | *(isi: prompting terarah / fine-tuning ringan LoRA)* |
| **Alternatif dipertimbangkan** | Prompting terarah dengan LLM API vs fine-tuning ringan (LoRA/PEFT) pada model bahasa kecil open-source |
| **Alasan** | *(isi setelah dapat klarifikasi panitia soal definisi "wajib di-fine-tune" — lihat item terbuka di bawah)* |
| **Diputuskan oleh** | *(isi nama/tim)* |
| **Status** | ⏳ Menunggu klarifikasi panitia (ditanyakan via Discord AIC) |

### 007 — Tech stack backend & frontend

| Field | Isi |
|---|---|
| **Tanggal** | *(isi tanggal)* |
| **Keputusan** | FastAPI (backend), React sederhana atau HTML+JS statis (frontend) |
| **Alternatif dipertimbangkan** | Flask/Django untuk backend; framework frontend yang lebih berat |
| **Alasan** | FastAPI ringan & cepat setup dengan dokumentasi API otomatis; frontend sengaja disederhanakan karena batasan MVP rulebook hanya membutuhkan satu alur input-output, bukan aplikasi multi-halaman |
| **Diputuskan oleh** | *(isi nama/tim)* |
| **Status** | Diusulkan |

---

## Template untuk Keputusan Baru

Salin blok ini setiap kali menambah keputusan baru:

```
### 0XX — [Judul singkat keputusan]

| Field | Isi |
|---|---|
| **Tanggal** | |
| **Keputusan** | |
| **Alternatif dipertimbangkan** | |
| **Alasan** | |
| **Diputuskan oleh** | |
| **Status** | Diusulkan / Final / Dibatalkan |
```

---

## Item Terbuka yang Menunggu Keputusan/Klarifikasi

- [ ] Sektor manufaktur final (#004)
- [ ] Konfirmasi definisi "fine-tune" dari panitia AIC, menentukan hasil #006
- [ ] Validasi tech stack setelah eksperimen awal (#005, #007)
- [ ] Sumber harga komoditas global — dipakai atau tidak (lihat Data Dictionary bagian 1.4)
