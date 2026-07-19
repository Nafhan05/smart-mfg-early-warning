# Data README
## Sistem Peringatan Dini Biaya Bahan Baku Manufaktur

### Sumber Data

| Sumber | Deskripsi | Cara Akses | Format |
|---|---|---|---|
| BPS Ekspor-Impor | Data nilai & volume impor bahan baku | https://www.bps.go.id | Excel/CSV |
| BPS IHPB | Indeks Harga Perdagangan Besar Bahan Baku | https://www.bps.go.id | Excel/CSV |
| Bank Indonesia | Kurs USD/IDR historis | https://www.bi.go.id | CSV |

### Langkah Memperoleh Data

1. **BPS Ekspor-Impor:**
   - Kunjungi https://www.bps.go.id
   - Cari "Ekspor Impor" atau "Perdagangan Luar Negeri"
   - Filter berdasarkan kode HS yang relevan dengan sektor Makanan-Minuman
   - Unduh dalam format Excel/CSV
   - Simpan ke `data/raw/`

2. **BPS IHPB:**
   - Kunjungi https://www.bps.go.id
   - Cari "Indeks Harga Perdagangan Besar"
   - Filter berdasarkan sektor terpilih
   - Unduh data historis bulanan
   - Simpan ke `data/raw/`

3. **Kurs USD/IDR:**
   - Kunjungi https://www.bi.go.id
   - Cari "Kurs" atau "Exchange Rate"
   - Unduh data historis kurs tengah
   - Simpan ke `data/raw/`

### Kode HS untuk Sektor Makanan-Minuman

*(Belum diputuskan — akan ditentukan setelah diskusi tim)*

Contoh kode HS yang mungkin relevan:
- 1101: Tepung gandum
- 1701: Gula
- 1509: Minyak zaitun
- 0901: Kopi
- 0803: Pisang

### Format Data yang Diharapkan

- Semua data harus dalam format bulanan (YYYY-MM)
- Kolom minimal: `periode`, `nilai`, `volume` (jika ada)
- Missing values ditandai dengan NaN
- Data mentah disimpan apa adanya di `data/raw/`
- Data bersih (hasil cleaning) disimpan di `data/processed/`

### Catatan Penting

- Jangan edit file di `data/raw/` — data mentah harus tetap asli
- Semua processing dilakukan di `data/processed/`
- Update dokumen ini setiap kali menambah sumber data baru
