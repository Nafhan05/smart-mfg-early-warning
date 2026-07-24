# Data README
## Sistem Peringatan Dini Biaya Bahan Baku Manufaktur

### Ringkasan

Dokumen ini menjelaskan cara memperoleh data mentah untuk proyek prediksi IHPB Bahan Baku sektor Makanan-Minuman.

---

### 1. Sumber Data

| Sumber | Deskripsi | Akses | Status |
|---|---|---|---|
| **BPS WebAPI** | Data Ekspor-Impor & IHPB | https://webapi.bps.go.id | ⚠️ Perlu daftar API key |
| **BPS Portal** | Data Ekspor-Impor | https://www.bps.go.id/id/exim | ✅ Bisa diakses |
| **Bank Indonesia** | Kurs USD/IDR (JISDOR) | https://www.bi.go.id | ⚠️ Perlu cari URL alternatif |

---

### 2. BPS WebAPI (Rekomendasi Utama)

**Mengapa pakai WebAPI?**
- Lebih efisien untuk download data historis bulk
- Format JSON yang mudah diproses
- Tersedia data dari 2010 ke atas

**Cara Pakai:**

1. **Daftar akun:**
   ```
   https://webapi.bps.go.id/developer/
   ```

2. **Dapatkan API key token** (2-3 token per akun)

3. **Gunakan endpoint:**
   ```
   GET https://webapi.bps.go.id/v1/api/list/
   ```

4. **Parameter penting:**
   | Parameter | Keterangan | Contoh |
   |---|---|---|
   | `model` | Tipe data | "data" untuk data dinamis |
   | `domain` | Wilayah | "0000" untuk nasional |
   | `var` | Variable ID | Perlu dicari untuk Ekspor-Impor & IHPB |
   | `th` | Periode | 1=tahunan, 2:3=bulanan |
   | `key` | API key | Token yang didaftarkan |

---

### 3. Data Ekspor-Impor

**Portal Alternatif:**
```
https://www.bps.go.id/id/exim
```

**Cara Manual (jika tidak pakai WebAPI):**
1. Kunjungi portal di atas
2. Filter berdasarkan:
   - **Jenis**: Impor
   - **Periode**: Bulanan
   - **Kode HS**: Sesuai sektor (lihat bawah)
3. Download dalam format Excel/CSV
4. Simpan ke `data/raw/`

---

### 4. Data IHPB Bahan Baku

**Akses:**
- Melalui WebAPI BPS dengan variable ID untuk IHPB
- Perlu eksplorasi untuk menemukan variable ID yang tepat

**Target:**
- Indeks bulanan per sektor (Makanan-Minuman)
- Historis sejak 2010

---

### 5. Data Kurs USD/IDR

**Sumber:** Bank Indonesia

**Jenis Kurs:**
- **JISDOR**: Kurs acuan harian (Jakarta Interbank Spot Dollar Rate)
- **Kurs Transaksi BI**: Kurs jual/beli

**Alternatif Akses:**
- Download CSV dari portal BI
- Gunakan sumber data kurs dari Yahoo Finance atau sumber lain

---

### 6. Kode HS untuk Sektor Makanan-Minuman

**Kode HS yang Relevan:**

| Kode HS | Komoditas | Keterangan |
|---|---|---|
| 1101 | Tepung gandum | Bahan baku roti, mie |
| 1701, 1702 | Gula | Gula pasir, gula cristal |
| 1509, 1511 | Minyak nabati | Minyak zaitun, kelapa sawit |
| 0901 | Kopi | Biji kopi |
| 0902 | Teh | Teh hitam, teh hijau |
| 0401, 0402 | Susu | Susu cair, susu bubuk |
| 0201, 0202 | Daging sapi | Daging segar/bebeku |
| 0301, 0302, 0303 | Ikan | Ikan segar/bebeku |

**Catatan:**
- Pilih 2-3 kode HS utama yang paling relevan
- Pastikan ada data historis yang cukup untuk training

---

### 7. Format Data yang Diharapkan

**Input untuk Model:**
- Format: Bulanan (YYYY-MM)
- Kolom minimal: `periode`, `nilai`, `volume` (jika ada)
- Missing values ditandai dengan NaN

**Penyimpanan:**
- `data/raw/`: Data mentah (jangan diedit)
- `data/processed/`: Data bersih siap training

---

### 8. Langkah Selanjutnya

1. **Daftar WebAPI BPS** → dapatkan API key
2. **Eksplorasi variable ID** untuk Ekspor-Impor dan IHPB
3. **Download sample data** → validasi format
4. **Tentukan kode HS final** → diskusi tim
5. **Update dokumen ini** dengan temuan

---

### 9. Catatan Penting

- **Tidak perlu auto-update**: Download sekali saat development
- **Model sudah pre-trained**: Data historis untuk training, bukan real-time
- **Pastikan bulanan**: Semua sumber dalam format YYYY-MM
- **Konsistensi satuan**: Pastikan satuan volume sama di seluruh dataset

---

*Terakhir diperbarui: 24 Juli 2026*
