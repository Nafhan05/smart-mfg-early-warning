# Individual Task Breakdown
## Sistem Peringatan Dini Biaya Bahan Baku Manufaktur — COMPFEST 18 AIC

Dokumen ini memecah roadmap 6 minggu (lihat Team Guide, Bagian 6) menjadi tugas konkret per orang per minggu, lengkap dengan **Definisi Selesai (Definition of Done)** supaya jelas kapan suatu tugas benar-benar bisa dicentang, bukan sekadar "udah dikerjain tapi belum jelas hasilnya apa".

**Cara pakai:** tiap orang cek bagian perannya masing-masing tiap minggu. Centang tugas yang selesai. Kalau ada tugas yang nggak selesai di minggu itu, bawa ke stand-up/sinkronisasi mingguan tim, jangan dibiarkan menumpuk diam-diam.

**Pemetaan peran** (samakan dengan Team Guide):
- **P1** — Data & Riset (Data Lead)
- **P2** — Machine Learning Engineer
- **P3** — Backend & Agent Engineer
- **P4** — Frontend & Product/Presentation Lead

---

## Minggu 1 (14–20 Juli) — Setup & Scoping

### P1 — Data & Riset
- [ ] Fasilitasi diskusi tim untuk mengunci sektor final (kandidat: tekstil vs industri berbasis gandum) — lihat Decision Log #004
  - *Selesai jika:* keputusan tercatat di Decision Log dengan alasan yang jelas
- [ ] Buka & eksplorasi langsung data mentah BPS Ekspor-Impor dan IHPB Bahan Baku (bukan cuma baca artikel/ringkasan)
  - *Selesai jika:* minimal satu file/tabel data mentah berhasil diunduh dan dibuka, formatnya (CSV/Excel/HTML/PDF) sudah diketahui
- [ ] Update Data Dictionary sesuai struktur data asli yang ditemukan (bukan lagi perkiraan)
  - *Selesai jika:* kolom-kolom di Data Dictionary sudah dicoret/disesuaikan dengan nama & format kolom sebenarnya
- [ ] Cek ketersediaan data kurs USD/IDR dari BI dan (jika perlu) harga komoditas global untuk sektor terpilih
  - *Selesai jika:* sumber data dan cara aksesnya sudah dikonfirmasi bisa dipakai

### P2 — Machine Learning Engineer
- [ ] Riset singkat pendekatan model time-series tabular yang cocok (gradient boosting) — baca dokumentasi LightGBM/XGBoost
  - *Selesai jika:* sudah punya rencana kasar arsitektur model & metrik evaluasi
- [ ] Siapkan environment training lokal (Python venv/conda, library terinstall)
  - *Selesai jika:* `pip install` seluruh dependency berjalan tanpa error

### P3 — Backend & Agent Engineer
- [ ] Setup repository GitHub (public), struktur folder awal sesuai Agent Guide Bagian 4
  - *Selesai jika:* repo sudah ada, struktur folder dasar (`data/`, `model/`, `backend/`, `frontend/`) sudah dibuat meski masih kosong
- [ ] Setup skeleton `docker-compose.yml` dan `Dockerfile` awal (boleh masih placeholder)
  - *Selesai jika:* `docker compose up` berjalan tanpa error meski aplikasinya belum ada isi
- [ ] Kirim pertanyaan klarifikasi soal ketentuan "fine-tune" ke Discord AIC
  - *Selesai jika:* pertanyaan sudah dikirim (lihat Decision Log #006 untuk redaksi pertanyaan)

### P4 — Frontend & Product/Presentation Lead
- [ ] Ikut serta dalam diskusi scoping sektor bersama tim
- [ ] Buat wireframe kasar tampilan aplikasi (bisa di kertas/Figma sederhana) — satu halaman, input dropdown sektor + tombol, area hasil
  - *Selesai jika:* ada gambaran visual yang disepakati tim, meski masih sketsa
- [ ] Siapkan draf awal poin-poin untuk Twibbon & poster pendaftaran sesuai ketentuan rulebook
  - *Selesai jika:* Twibbon sudah diunggah ke Instagram sesuai format yang diminta (hashtag, tag, mention)

---

## Minggu 2 (21–27 Juli) — Data Cleaning & Feature Engineering

### P1 — Data & Riset
- [ ] Bersihkan data mentah (handle missing values, samakan satuan, samakan granularitas waktu ke bulanan)
  - *Selesai jika:* ada file `data/processed/` yang siap dipakai, bebas dari data kosong/rusak yang tidak dijelaskan
- [ ] Lakukan EDA (exploratory data analysis): visualisasi tren IHPB, kurs, nilai impor dari waktu ke waktu
  - *Selesai jika:* ada notebook EDA dengan minimal 3-5 grafik kunci + catatan insight singkat
- [ ] Ikuti AIC Talks (25 Juli) dan catat insight yang relevan
  - *Selesai jika:* kehadiran tercatat (untuk bonus penilaian) + ada catatan ringkas dibagikan ke tim

### P2 — Machine Learning Engineer
- [ ] Rancang & implementasikan feature engineering (lag features, rolling volatility, dsb — lihat Data Dictionary Bagian 2), bekerja sama dengan P1
  - *Selesai jika:* fungsi/script feature engineering (`model/features.py`) berjalan dan menghasilkan tabel fitur dari data bersih
- [ ] Buat train-test split berbasis waktu (time-based split)
  - *Selesai jika:* data terbagi jelas jadi periode train dan periode test, tidak ada kebocoran data ke masa depan

### P3 — Backend & Agent Engineer
- [ ] Riset & putuskan pendekatan agent: prompting terarah vs fine-tuning ringan (LoRA) — update Decision Log #006 begitu ada jawaban panitia
  - *Selesai jika:* keputusan final tercatat dengan alasan
- [ ] Mulai desain schema request/response API (`backend/schemas.py`) sesuai Agent Guide Bagian 7
  - *Selesai jika:* schema Pydantic untuk `/predict` sudah didefinisikan meski endpoint belum berfungsi penuh

### P4 — Frontend & Product/Presentation Lead
- [ ] Mulai setup project frontend (React/HTML sederhana), bangun struktur halaman kosong sesuai wireframe
  - *Selesai jika:* halaman bisa dibuka di browser lokal, walau belum terhubung ke backend
- [ ] Mulai kumpulkan referensi visual/gaya untuk video promosi nanti (mood board sederhana)

---

## Minggu 3 (28 Juli – 3 Agustus) — Model Baseline

### P1 — Data & Riset
- [ ] Bantu validasi kualitas fitur bersama P2, cek apakah ada anomali data yang mempengaruhi hasil model
- [ ] Mulai kumpulkan/tulis draf "Alur Memperoleh Dataset" untuk proposal

### P2 — Machine Learning Engineer
- [ ] Latih model baseline (gradient boosting) untuk horizon 1-3 bulan
  - *Selesai jika:* model tersimpan (`model/model.pkl`) dan bisa menghasilkan prediksi dari input fitur
- [ ] Evaluasi model dengan MAE/RMSE dan directional accuracy, bandingkan ke baseline naif (misal: prediksi = nilai bulan lalu)
  - *Selesai jika:* ada tabel/grafik hasil evaluasi yang menunjukkan model lebih baik dari baseline naif — kalau belum, catat kenapa & rencana perbaikan
- [ ] Ekstrak feature importance dari model untuk dipakai agent nanti
  - *Selesai jika:* ada daftar fitur paling berpengaruh, siap dipakai P3

### P3 — Backend & Agent Engineer
- [ ] Bangun endpoint `/predict` dasar (FastAPI) yang bisa load `model.pkl` dan mengembalikan prediksi mentah (belum ada penjelasan agent)
  - *Selesai jika:* endpoint bisa dites via `/docs` (Swagger UI) dan mengembalikan angka prediksi
- [ ] Bangun endpoint `/health`
  - *Selesai jika:* mengembalikan status OK

### P4 — Frontend & Product/Presentation Lead
- [ ] Hubungkan frontend ke endpoint `/predict` (tampilkan angka mentah dulu, styling belakangan)
  - *Selesai jika:* input dari form berhasil memicu request dan menampilkan response di halaman
- [ ] Susun outline proposal PDF (kerangka bab sesuai template rulebook)
  - *Selesai jika:* outline dengan judul tiap bagian sudah dibagikan ke tim untuk diisi bertahap

---

## Minggu 4 (4–10 Agustus) — Agent & Integrasi Backend

### P1 — Data & Riset
- [ ] Bantu siapkan beberapa skenario historis konkret (kejadian nyata di masa lalu) untuk dipakai sebagai contoh demo & video
  - *Selesai jika:* ada 2-3 skenario historis dengan angka & narasi yang jelas

### P2 — Machine Learning Engineer
- [ ] Refinement model (tuning hyperparameter, coba fitur tambahan jika perlu) berdasarkan hasil evaluasi Minggu 3
  - *Selesai jika:* ada peningkatan metrik terukur dari versi baseline, atau kesimpulan jelas kenapa versi baseline sudah cukup baik
- [ ] Finalisasi model untuk dipakai versi demo (freeze model, jangan diubah-ubah lagi mendekati deadline)
  - *Selesai jika:* `model.pkl` final sudah ditandai sebagai versi yang dipakai submission

### P3 — Backend & Agent Engineer
- [ ] Implementasikan lapisan agent (`backend/agent.py`) sesuai keputusan Minggu 2 — panggil LLM API dengan konteks dari output model
  - *Selesai jika:* endpoint `/predict` sudah mengembalikan `key_drivers` dan `recommendation`, bukan cuma angka mentah
- [ ] Integrasikan API key LLM lewat `.env`, pastikan tidak ter-hardcode
  - *Selesai jika:* `.env.example` ada di repo, `.env` asli masuk `.gitignore`

### P4 — Frontend & Product/Presentation Lead
- [ ] Update tampilan frontend untuk menampilkan hasil lengkap (arah, faktor pendorong, rekomendasi) dengan styling yang layak
  - *Selesai jika:* tampilan sudah bisa didemokan tanpa terlihat "mentah"
- [ ] Mulai tulis storyboard/script untuk video proof of work dan video promosi

---

## Minggu 5 (11–17 Agustus) — Integrasi End-to-End (Seluruh Tim Terlibat)

### Seluruh Tim
- [ ] Uji alur penuh dari frontend → backend → model → agent → tampil ke pengguna, di lingkungan lokal masing-masing
  - *Selesai jika:* alur berjalan tanpa error dari awal sampai akhir
- [ ] Jalankan `docker compose up` dari clone repository yang bersih (bukan folder development yang sudah dipakai lama)
  - *Selesai jika:* aplikasi bisa jalan hanya dengan mengikuti README, tanpa langkah tersembunyi yang cuma diketahui satu orang
- [ ] Cross-check tidak ada elemen yang menunjukkan identitas institusi di repo/README/kode

### P1 — Data & Riset
- [ ] Finalisasi bagian data & metodologi untuk proposal

### P2 — Machine Learning Engineer
- [ ] Siapkan grafik/tabel hasil evaluasi model final untuk dilampirkan ke proposal & video

### P3 — Backend & Agent Engineer
- [ ] Perbaiki bug yang ditemukan saat integrasi, pastikan `README.md` sudah lengkap dan bisa diikuti orang lain

### P4 — Frontend & Product/Presentation Lead
- [ ] Finalisasi UI, siapkan seluruh skenario demo yang akan direkam di video

---

## Minggu 6 (18–24 Agustus) — Polishing & Deliverables

### Seluruh Tim
- [ ] Review silang proposal PDF (semua bagian sudah terisi, ≤20 halaman di luar cover/lampiran)
- [ ] Uji ulang `docker compose up` sekali lagi dari environment bersih (final check)
- [ ] Review commit history — pastikan mengikuti Conventional Commits sepanjang perjalanan
- [ ] Pastikan repo GitHub berstatus public

### P1 — Data & Riset
- [ ] Finalisasi & rapikan `data/README.md` dan Data Dictionary versi akhir

### P2 — Machine Learning Engineer
- [ ] Bantu isi bagian metodologi teknis proposal terkait model

### P3 — Backend & Agent Engineer
- [ ] Commit & push terakhir sebelum 25 Agustus 23.55 WIB — cek ulang deadline commit terakhir sesuai rulebook

### P4 — Frontend & Product/Presentation Lead
- [ ] Rekam, edit, dan upload video proof of work (≤7 menit, unlisted) dan video promosi (≤5 menit, public) dengan format nama sesuai ketentuan rulebook
- [ ] Submit seluruh berkas (repo, video, proposal) melalui situs COMPFEST sebelum deadline

---

## Setelah Submit (9–11 September)

### Seluruh Tim
- [ ] Standby di Discord tanggal 9–10 September pukul 20.00 untuk kemungkinan diminta klarifikasi/live demo
- [ ] Pantau pengumuman finalis 11 September di Instagram COMPFEST

---

## Catatan Penggunaan Dokumen

- Tugas yang tercantum di sini adalah **perkiraan awal** berdasarkan roadmap yang sudah disusun — sesuaikan lagi setelah tim benar-benar mulai kerja dan menemukan kendala nyata (misalnya data lebih sulit didapat dari perkiraan, atau satu peran butuh bantuan ekstra di minggu tertentu).
- Kalau satu tugas ternyata jauh lebih berat dari perkiraan, angkat di sinkronisasi mingguan tim secepatnya — jangan tunggu sampai Minggu 5 baru ketahuan ada yang tertinggal jauh.
- Dokumen ini melengkapi, bukan menggantikan, Team Guide (untuk gambaran besar) dan Decision Log (untuk alasan keputusan).
