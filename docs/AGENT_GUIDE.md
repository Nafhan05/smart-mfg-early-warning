# Panduan Teknis untuk AI Coding Agent
## Proyek: Sistem Peringatan Dini Biaya Bahan Baku Manufaktur
### COMPFEST 18 — AI Innovation Challenge (Pilar: Smart Manufacturing)

Dokumen ini adalah spesifikasi kerja untuk AI agent yang mengerjakan bagian coding proyek. Baca seluruh dokumen sebelum mulai menulis kode. Ikuti batasan scope dengan ketat — kompetisi ini menilai kematangan arsitektur, bukan jumlah fitur.

---

## 1. Ringkasan Proyek

Sistem meramal pergerakan **Indeks Harga Perdagangan Besar (IHPB) Bahan Baku** untuk satu sektor manufaktur terpilih, 1–3 bulan ke depan, lalu menjelaskan faktor pendorongnya dan memberi rekomendasi aksi ke pengguna (pelaku industri manufaktur skala menengah).

Sistem terdiri dari dua komponen AI yang terpisah bersih:
1. **Model prediktif** — model ML tradisional (bukan LLM) yang dilatih dari data historis untuk memprediksi angka indeks.
2. **Agent penjelas** — komponen berbasis LLM yang menerima output model + fitur pendukung, lalu menghasilkan narasi penjelasan dan rekomendasi.

**Alur pengguna (single input → single output, sesuai batasan MVP):**
Pengguna memilih sektor (bisa fixed/dropdown, tidak perlu banyak sektor) dan menekan tombol "Ramalkan" → sistem menampilkan: angka prediksi, arah pergerakan (naik/turun/stabil), faktor pendorong utama, dan rekomendasi aksi.

---

## 2. Batasan Scope — WAJIB DIPATUHI

Ini bukan saran, ini syarat kelulusan babak penyisihan dari rulebook kompetisi. Jangan over-engineer.

| Layer | Boleh | Dilarang di tahap penyisihan |
|---|---|---|
| Frontend | Satu alur interaksi inti: input tunggal → output AI | Dashboard analitik lanjutan, sistem autentikasi kompleks, halaman riwayat |
| Backend | Pemrosesan sinkron (request → response langsung) | Background jobs, pipeline pencatatan data otomatis (auto data logging), database terdistribusi |
| Model AI | Inferensi inti (core inference) dengan parameter **statis** saat demo | Sistem auto-tuning, bulk testing scripts, feedback loop otomatis |

**Implikasi konkret untuk agent coding:**
- Jangan bangun scheduler/cron job yang menarik data BPS otomatis tiap bulan. Data historis ditarik & diproses **sekali** saat development, disimpan sebagai file lokal (CSV/Parquet), lalu dipakai untuk training. Saat demo, model sudah pre-trained dan tinggal load.
- Jangan bangun sistem retraining otomatis. Model di-training sekali via script, hasilnya (file model, misal `.pkl` atau `.joblib`) disimpan di repo atau dimuat saat container start.
- Jangan bangun user authentication/login system apa pun.
- API cukup **satu endpoint utama** yang menerima parameter (sektor, horizon waktu) dan mengembalikan hasil prediksi + penjelasan dalam satu response.

---

## 3. Tech Stack yang Direkomendasikan

Pilihan ini mengutamakan kecepatan development untuk tim kecil dengan waktu terbatas (~6 minggu), bukan yang paling canggih.

- **Model prediktif:** Python, `scikit-learn` / `lightgbm` / `xgboost` untuk model tabular time-series (gradient boosting). Hindari deep learning (LSTM/Transformer) kecuali tim punya waktu lebih dan data cukup panjang — gradient boosting jauh lebih cepat dikembangkan dan dievaluasi untuk dataset bulanan yang relatif pendek.
- **Backend API:** Python + `FastAPI` (ringan, cepat setup, otomatis menghasilkan dokumentasi API di `/docs`).
- **Agent penjelas:** panggilan ke LLM API (lihat Bagian 6 soal opsi fine-tuning vs prompting) menggunakan Anthropic API atau OpenAI API, dipanggil dari backend.
- **Frontend:** React sederhana atau bahkan HTML+JS statis dengan satu form dan satu area hasil — tidak perlu framework berat, tidak perlu state management library, mengingat batasan scope MVP.
- **Containerization:** Docker + `docker-compose.yml` yang menjalankan backend (dan frontend jika dipisah container) dengan satu perintah `docker compose up`.
- **Penyimpanan data:** file lokal (CSV/Parquet) di dalam repo untuk dataset yang sudah diproses — tidak perlu database (Postgres/MongoDB dst) kecuali tim merasa sangat perlu; untuk MVP sekecil ini, file lokal + in-memory load saat startup sudah cukup.

---

## 4. Struktur Repository

```
repo-root/
├── README.md                     # setup guide — WAJIB jelas & lengkap
├── docker-compose.yml
├── .env.example                  # contoh env vars (API keys dsb), JANGAN commit .env asli
├── data/
│   ├── raw/                      # data mentah hasil scraping/download (BPS, IHPB, kurs)
│   ├── processed/                # data bersih siap training (hasil feature engineering)
│   └── README.md                 # jelaskan sumber & cara memperoleh tiap file data
├── notebooks/                    # eksplorasi data (EDA), boleh Jupyter notebook, TIDAK di-deploy
├── model/
│   ├── train.py                  # script training model, dijalankan manual sekali
│   ├── model.pkl                 # model hasil training yang sudah jadi (artifact)
│   ├── features.py               # definisi feature engineering, dipakai ulang saat inference
│   └── evaluate.py               # script backtesting/evaluasi akurasi
├── backend/
│   ├── main.py                   # entry point FastAPI
│   ├── predictor.py              # load model.pkl, fungsi predict()
│   ├── agent.py                  # logic pemanggilan LLM untuk penjelasan & rekomendasi
│   ├── schemas.py                # request/response models (Pydantic)
│   └── requirements.txt
├── frontend/
│   ├── src/ ...                  # single-page app sederhana
│   └── package.json
└── docs/
    └── architecture.md           # diagram/penjelasan arsitektur untuk dilampirkan ke proposal
```

Sesuaikan detail nama file, tapi pertahankan pemisahan jelas antara `data/`, `model/`, `backend/`, `frontend/` — ini yang dinilai sebagai "modularitas arsitektur" oleh juri.

---

## 5. Spesifikasi Data & Model

### 5.1 Sumber data (isi setelah tim mengunci sektor)

| Sumber | Cara akses | Catatan teknis |
|---|---|---|
| BPS Ekspor-Impor | Tabel statistik / publikasi bulanan di bps.go.id, atau Web API BPS jika tersedia untuk indikator yang dibutuhkan | Kemungkinan perlu parsing tabel Excel/PDF — sisihkan waktu eksplorasi di awal sebelum komit ke format tertentu |
| IHPB Bahan Baku | Tabel statistik BPS per sektor, bulanan sejak 2010 | Ini adalah **target/label** untuk model, bukan sekadar fitur |
| Kurs USD/IDR | Data historis Bank Indonesia | Biasanya tersedia rapi dalam format tabel/CSV |

> **Catatan untuk agent:** sektor spesifik yang dipilih tim akan menentukan HS code dan kategori IHPB yang relevan. Jangan asumsikan nama kolom/kategori tanpa konfirmasi — cek dulu struktur data asli sebelum menulis pipeline parsing yang kaku.

### 5.2 Target variabel

`IHPB_bahan_baku_sektor_X` (indeks bulanan) pada waktu `t + horizon`, di mana `horizon` = 1 sampai 3 bulan ke depan.

### 5.3 Fitur yang disarankan

- Lag values dari IHPB itu sendiri (`t-1`, `t-3`, `t-6`)
- Kurs USD/IDR (level dan perubahan %)
- Nilai/volume impor bulanan sektor terkait (dan perubahannya)
- Indikator konsentrasi negara asal impor (opsional, jika data memungkinkan)
- Fitur musiman (bulan, jarak ke Lebaran/Nataru jika relevan ke sektor)

### 5.4 Model & evaluasi

- Gunakan **regresi** (bukan klasifikasi) untuk memprediksi nilai indeks, atau prediksi **perubahan %** dari nilai saat ini (sering lebih stabil untuk time-series pendek).
- Split data secara **time-based** (train pada periode awal, test pada periode akhir) — JANGAN random split, karena ini time-series dan random split akan bocor informasi masa depan ke training.
- Metrik evaluasi: MAE dan/atau RMSE, plus directional accuracy (seberapa sering arah naik/turun diprediksi benar — ini metrik yang lebih mudah dijelaskan ke juri non-teknis).
- Simpan hasil evaluasi (angka + grafik prediksi vs aktual) untuk dipakai di proposal dan video.

---

## 6. Spesifikasi Agent Penjelas

**Input ke agent:** output numerik model (nilai prediksi, arah, confidence/margin jika ada) + fitur-fitur pendukung yang paling berpengaruh (misal dari feature importance model).

**Output agent:** teks singkat berisi (a) ringkasan prediksi dalam bahasa manusia, (b) 1-2 faktor pendorong utama, (c) rekomendasi aksi konkret (stocking, cari substitusi, kontrak forward — pilih yang paling sesuai konteks).

**Cara implementasi (dua opsi, pilih salah satu, dokumentasikan alasannya di proposal):**

1. **Prompting terarah (lebih cepat dikerjakan):** panggil LLM API dengan system prompt yang jelas + few-shot examples, masukkan angka-angka dari model sebagai konteks di user message. Tidak melibatkan training ulang parameter model.
2. **Fine-tuning ringan (LoRA/PEFT) pada model bahasa kecil open-source:** latih adapter kecil di atas model seperti Llama/Mistral/Gemma versi kecil, menggunakan beberapa ratus contoh instruksi-jawaban yang dibuat tim dari skenario historis data. Ini genuinely "fine-tuning" dalam arti teknis penuh.

> **Penting:** rulebook kompetisi menyebut "model wajib di-fine-tune sesuai inovasi fitur tim" — tim masih menunggu klarifikasi panitia apakah ini berlaku ke seluruh komponen AI atau cukup ke model prediktif utama. Sambil menunggu jawaban, agent coding boleh mulai dengan opsi 1 (prompting) untuk kecepatan development, tapi struktur kode sebaiknya dibuat **modular** sehingga mudah diganti ke opsi 2 jika diperlukan (pisahkan logic pemanggilan LLM ke satu file/fungsi, jangan hardcode di banyak tempat).

---

## 7. Spesifikasi API Backend

Satu endpoint utama sudah cukup untuk MVP.

```
POST /predict
```

**Request body (contoh):**
```json
{
  "sector": "tekstil",
  "horizon_months": 2
}
```

**Response body (contoh):**
```json
{
  "sector": "tekstil",
  "horizon_months": 2,
  "current_index": 118.4,
  "predicted_index": 126.9,
  "predicted_change_pct": 7.2,
  "direction": "naik",
  "key_drivers": [
    "Pelemahan rupiah terhadap dolar AS",
    "Penurunan volume impor kapas dari negara asal utama"
  ],
  "recommendation": "Pertimbangkan pembelian stok kapas dalam waktu dekat atau eksplorasi alternatif serat lokal untuk mengurangi eksposur terhadap kenaikan harga."
}
```

Sesuaikan nama field sesuai kebutuhan tim, tapi pertahankan prinsip: satu request, satu response lengkap, tanpa perlu polling/streaming/async job untuk MVP ini.

Tambahkan endpoint `GET /health` sederhana untuk memudahkan panitia/juri mengecek service hidup saat verifikasi.

---

## 8. Spesifikasi Frontend

- Satu halaman.
- Input: dropdown/select sektor (isi sesuai sektor yang tim kunci — 1-2 opsi saja tidak masalah), input horizon waktu (bisa fixed ke 2 bulan jika ingin lebih sederhana lagi).
- Tombol submit → panggil `POST /predict` → tampilkan hasil di bawahnya (angka prediksi, arah dengan indikator visual sederhana seperti panah/warna, daftar faktor pendorong, rekomendasi).
- Tidak perlu routing multi-halaman, tidak perlu state management kompleks, tidak perlu loading skeleton canggih — cukup indikator loading sederhana saat menunggu response.

---

## 9. Docker & Setup

- `docker-compose.yml` harus bisa menjalankan seluruh sistem (backend minimal, frontend jika di-containerize) dengan satu perintah: `docker compose up`.
- `README.md` di root wajib memuat:
  - Penjelasan singkat proyek (2-3 kalimat)
  - Prasyarat (Docker version, dsb.)
  - Langkah instalasi & menjalankan (`docker compose up`, port yang dipakai)
  - Cara mengakses aplikasi setelah running (URL/port)
  - Penjelasan singkat struktur folder
  - Catatan bahwa model sudah pre-trained (jelaskan cara re-train jika reviewer ingin, walau tidak wajib dijalankan ulang saat demo)
- API key (untuk LLM agent) **jangan** di-hardcode atau di-commit. Gunakan `.env` (masuk `.gitignore`) dan sediakan `.env.example` sebagai contoh format.

---

## 10. Konvensi Commit

Gunakan **Conventional Commits** — ini syarat eksplisit dari rulebook, commit yang tidak mengikuti format bisa dianggap tidak memenuhi standar.

```
feat: tambah endpoint prediksi IHPB sektor tekstil
fix: perbaiki parsing tanggal pada data BPS
refactor: pisahkan logic agent ke modul terpisah
```

Commit dan push dilakukan bertahap sepanjang periode pengerjaan (bukan satu commit besar di akhir) — riwayat commit yang wajar dan progresif juga bagian dari yang dinilai panitia.

---

## 11. Larangan Identitas Institusi

Jangan mencantumkan nama kampus/institusi di mana pun — nama repository, README, komentar kode, nama file, video, atau proposal. Gunakan nama tim/proyek saja.

---

## 12. Checklist Sebelum Submit (untuk agent verifikasi ulang)

- [ ] `docker compose up` berhasil dijalankan dari clone repository yang bersih (bukan dari environment development yang sudah ada dependency ter-install manual)
- [ ] Endpoint `/predict` mengembalikan response valid untuk sektor yang didukung
- [ ] Model artifact (`model.pkl` atau setara) ikut ter-commit atau ter-generate otomatis saat build — jangan sampai container gagal jalan karena file model hilang
- [ ] `.env` asli TIDAK ter-commit; `.env.example` ADA
- [ ] Tidak ada nama institusi di mana pun dalam repo
- [ ] README lengkap dan bisa diikuti orang yang belum pernah melihat proyek ini sama sekali
- [ ] Commit history mengikuti Conventional Commits
- [ ] Repository berstatus **public** di GitHub

---

## 13. Hal yang Sengaja Belum Difinalkan (isi begitu tim memutuskan)

- [ ] Sektor manufaktur yang dipilih: ________________
- [ ] Horizon waktu prediksi final: ________________
- [ ] Opsi agent (prompting vs fine-tuning ringan): ________________
- [ ] LLM API yang dipakai (dan API key/environment variable terkait): ________________

Agent coding sebaiknya menahan diri dari hardcoding asumsi di atas terlalu dalam ke banyak file — sentralisasi konfigurasi ini di satu file config (misal `config.py` atau `.env`) supaya mudah diubah begitu keputusan final tim keluar.
