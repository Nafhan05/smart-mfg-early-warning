# Data Dictionary
## Sistem Peringatan Dini Biaya Bahan Baku Manufaktur — COMPFEST 18 AIC

Dokumen ini mendefinisikan setiap kolom/field data yang dipakai di proyek, dari data mentah sampai fitur siap-training. Update dokumen ini setiap kali menambah/mengubah sumber data atau fitur — jangan biarkan dokumen ini basi, karena inilah rujukan bersama tim supaya semua orang (Data Lead, ML Engineer, Backend Engineer) memakai definisi yang sama.

Isi bagian **[ISI SETELAH SEKTOR DIKUNCI]** begitu tim sudah menentukan sektor manufaktur final.

---

## 1. Data Mentah (Raw Data)

### 1.1 Sumber: BPS — Ekspor-Impor

| Kolom | Deskripsi | Tipe | Satuan | Contoh Nilai | Catatan |
|---|---|---|---|---|---|
| `periode` | Bulan-tahun pencatatan | date (YYYY-MM) | — | 2025-03 | Granularitas bulanan |
| `kode_hs` | Kode klasifikasi Harmonized System untuk komoditas | string | — | 5201.00 | Tentukan digit HS yang dipakai (2/4/6 digit) — semakin detail, semakin sempit cakupan tapi semakin presisi |
| `nama_komoditas` | Nama komoditas sesuai kode HS | string | — | Kapas, tidak digaruk atau disisir | Ambil dari tabel referensi HS resmi |
| `negara_asal` | Negara asal impor | string | — | Amerika Serikat | Dipakai untuk hitung konsentrasi risiko negara asal |
| `pelabuhan_bongkar` | Pelabuhan tempat barang dibongkar | string | — | Tanjung Priok | Opsional, tergantung kebutuhan fitur |
| `nilai_impor_usd` | Nilai impor dalam dolar AS | float | USD | 1250000.00 | Sumber utama untuk fitur nilai impor |
| `volume_impor` | Volume/berat impor | float | kg / ton (samakan satuan) | 85000 | Pastikan satuan konsisten di seluruh dataset |
| **[ISI SETELAH SEKTOR DIKUNCI]** kode HS spesifik yang relevan untuk sektor terpilih | | | | | Daftar kode HS final akan menentukan filter data |

### 1.2 Sumber: BPS — Indeks Harga Perdagangan Besar (IHPB) Bahan Baku

| Kolom | Deskripsi | Tipe | Satuan | Contoh Nilai | Catatan |
|---|---|---|---|---|---|
| `periode` | Bulan-tahun pencatatan | date (YYYY-MM) | — | 2025-03 | Granularitas bulanan, historis sejak 2010 |
| `sektor` | Kelompok/seksi barang sesuai klasifikasi IHPB | string | — | Produk Makanan, Minuman dan Tembakau, Tekstil, Pakaian, dan Produk Kulit | **Ini yang jadi TARGET model** |
| `ihpb_bahan_baku` | Nilai indeks harga perdagangan besar bahan baku | float | indeks (basis tahun tertentu = 100) | 118.42 | Cek tahun dasar (base year) yang dipakai BPS saat ini, catat di sini |
| `perubahan_mtm_pct` | Perubahan bulanan (month-to-month) | float | % | 2.1 | Turunan/derived, hitung dari `ihpb_bahan_baku` |
| `perubahan_yoy_pct` | Perubahan tahunan (year-on-year) | float | % | 6.8 | Turunan/derived |

### 1.3 Sumber: Bank Indonesia — Kurs USD/IDR

| Kolom | Deskripsi | Tipe | Satuan | Contoh Nilai | Catatan |
|---|---|---|---|---|---|
| `periode` | Bulan-tahun (atau harian jika dipakai granular) | date | — | 2025-03 | Samakan granularitas dengan dataset lain (agregasi ke bulanan jika sumber asli harian) |
| `kurs_tengah` | Kurs tengah BI (rata-rata jual-beli) | float | IDR per USD | 16250 | Sumber acuan resmi |
| `kurs_perubahan_pct` | Perubahan kurs dari periode sebelumnya | float | % | -0.8 | Turunan/derived |

### 1.4 (Opsional) Sumber: Harga Komoditas Global

| Kolom | Deskripsi | Tipe | Satuan | Contoh Nilai | Catatan |
|---|---|---|---|---|---|
| `periode` | Bulan-tahun | date | — | 2025-03 | |
| `komoditas` | Nama komoditas global relevan (kapas, minyak nabati, dsb) | string | — | Kapas | Pilih sesuai sektor terpilih |
| `harga_global` | Harga komoditas di pasar internasional | float | USD per unit (sesuai standar komoditas) | 0.85 | Catat sumber spesifik (World Bank Pink Sheet, dsb) di sini setelah dipilih |

---

## 2. Data Hasil Proses (Processed / Model-Ready)

Tabel gabungan hasil join dari semua sumber di atas, per `periode` + `sektor`, siap dipakai untuk training.

| Kolom | Deskripsi | Tipe | Sumber Asal | Catatan |
|---|---|---|---|---|
| `periode` | Bulan-tahun | date | Semua sumber | Kunci join utama |
| `sektor` | Sektor manufaktur terpilih | string | IHPB | **[ISI SETELAH SEKTOR DIKUNCI]** |
| `ihpb_t` | Nilai IHPB pada bulan berjalan | float | IHPB | Basis perhitungan lag |
| `ihpb_lag1` | Nilai IHPB 1 bulan sebelumnya | float | Turunan dari IHPB | Fitur |
| `ihpb_lag3` | Nilai IHPB 3 bulan sebelumnya | float | Turunan dari IHPB | Fitur |
| `ihpb_lag6` | Nilai IHPB 6 bulan sebelumnya | float | Turunan dari IHPB | Fitur |
| `ihpb_rolling_std_3` | Standar deviasi IHPB 3 bulan terakhir (volatilitas) | float | Turunan dari IHPB | Fitur |
| `nilai_impor_total` | Total nilai impor bahan baku terkait sektor, bulan berjalan | float | Ekspor-Impor | Fitur |
| `nilai_impor_pct_change` | Perubahan % nilai impor dari bulan sebelumnya | float | Turunan dari Ekspor-Impor | Fitur |
| `konsentrasi_negara_asal` | Persentase impor dari negara asal dominan (misal top-1 negara / total) | float | Turunan dari Ekspor-Impor | Fitur — indikator risiko konsentrasi pasokan |
| `kurs_tengah` | Kurs tengah USD/IDR, bulan berjalan | float | BI | Fitur |
| `kurs_perubahan_pct` | Perubahan % kurs dari bulan sebelumnya | float | Turunan dari BI | Fitur |
| `bulan` | Bulan dalam angka (1-12), untuk menangkap pola musiman | int | Turunan dari `periode` | Fitur |
| `is_musim_ramai` | Flag periode menjelang Lebaran/Nataru (jika relevan ke sektor) | boolean/int (0/1) | Turunan manual | Fitur opsional |
| `target_ihpb_h1` | Nilai IHPB aktual 1 bulan ke depan (label untuk training horizon 1 bulan) | float | Turunan dari IHPB (shifted) | **TARGET** |
| `target_ihpb_h2` | Nilai IHPB aktual 2 bulan ke depan | float | Turunan dari IHPB (shifted) | **TARGET** |
| `target_ihpb_h3` | Nilai IHPB aktual 3 bulan ke depan | float | Turunan dari IHPB (shifted) | **TARGET** |

> Catatan penting: kolom `target_ihpb_hN` dibuat dengan **menggeser (shift)** data IHPB ke belakang sebanyak N periode. Pastikan proses ini dilakukan dengan hati-hati supaya tidak terjadi data leakage (jangan sampai fitur di baris tertentu mengandung informasi dari masa depan relatif terhadap targetnya).

---

## 3. Output API (Response Model)

Field yang dikembalikan oleh endpoint `/predict` — lihat juga Agent Guide bagian 7.

| Kolom | Deskripsi | Tipe |
|---|---|---|
| `sector` | Sektor yang diramal | string |
| `horizon_months` | Berapa bulan ke depan diramal | int |
| `current_index` | Nilai IHPB terkini (baseline) | float |
| `predicted_index` | Nilai IHPB hasil prediksi model | float |
| `predicted_change_pct` | Perubahan % dari `current_index` ke `predicted_index` | float |
| `direction` | Arah pergerakan: "naik" / "turun" / "stabil" | string |
| `key_drivers` | Daftar faktor pendorong utama (dari feature importance + interpretasi agent) | list of string |
| `recommendation` | Rekomendasi aksi dari agent | string |

---

## 4. Hal yang Masih Perlu Diisi Tim

- [ ] Sektor manufaktur final dan kode HS yang relevan
- [ ] Tahun dasar (base year) IHPB yang dipakai BPS saat data ditarik
- [ ] Satuan volume impor yang konsisten dipakai (kg/ton) dan sumber konversinya jika perlu
- [ ] Apakah memakai data harga komoditas global (bagian 1.4) atau tidak — tergantung sensitivitas sektor terpilih
- [ ] Definisi pasti "musim ramai" jika dipakai (bagian mana yang dianggap dekat Lebaran/Nataru)

Setiap kali salah satu poin di atas diputuskan, update dokumen ini juga — bukan cuma kode. Dokumen data yang basi lebih berbahaya daripada tidak ada dokumen sama sekali, karena orang bisa salah percaya pada informasi yang sudah tidak akurat.
