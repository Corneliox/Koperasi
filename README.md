# Koperasi Brimob - Sistem Manajemen Inventaris & Keuangan

Aplikasi desktop untuk manajemen inventaris, point of sale, pinjaman anggota, dan laporan keuangan untuk Koperasi Brimob.

## Fitur Utama

### 1. Manajemen Inventaris
- CRUD barang dengan kategori SEMBAKO dan TAKTIKAL
- Tracking mutasi stok (IN, OUT, RETURN, CORRECTION)
- Alert stok rendah
- Status barang (Koperasi/Konsinyasi)

### 2. Point of Sale (POS)
- Penjualan barang ke anggota
- Tracking transaksi per kategori
- Riwayat transaksi dengan filter

### 3. Manajemen Anggota
- Data anggota lengkap (Nama, Pangkat, NRP, Unit)
- Riwayat transaksi per anggota

### 4. Pinjaman Anggota
- Pencatatan pinjaman dengan bunga
- Tracking pembayaran angsuran
- Status pinjaman (Aktif, Lunas, Macet)

### 5. Laporan
- Export Excel (transaksi, inventaris, mutasi)
- Export PDF
- Filter berdasarkan periode dan anggota

## Instalasi

### Prasyarat
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Langkah Instalasi

1. Clone atau download repository ini

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Jalankan aplikasi:
```bash
python main.py
```

### Login Default
- **Username:** admin
- **Password:** admin123

## Build Executable (.exe)

Untuk membuat file executable:

```bash
python build_exe.py
```

File executable akan tersedia di folder `dist/KoperasiBrimob.exe`

## Struktur Folder

```
koperasi_brimob/
├── main.py                 # Entry point aplikasi
├── build_exe.py           # Script build PyInstaller
├── requirements.txt       # Dependencies
├── README.md             # Dokumentasi ini
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py  # Database schema & connection
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── warehouse.py   # CRUD warehouse/inventaris
│   │   ├── members.py     # CRUD anggota
│   │   ├── loans.py       # Manajemen pinjaman
│   │   └── transactions.py # Query transaksi
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── login_frame.py
│   │   ├── category_select_frame.py
│   │   ├── dashboard_frame.py
│   │   ├── store_frame.py
│   │   ├── history_frame.py
│   │   ├── members_frame.py
│   │   └── loans_frame.py
│   └── utils/
│       ├── __init__.py
│       └── export.py      # Export Excel & PDF
└── koperasi_brimob.db     # SQLite database (auto-created)
```

## Tech Stack

- **GUI:** CustomTkinter (Dark Theme)
- **Database:** SQLite3
- **Data Processing:** Pandas, OpenPyXL, XlsxWriter
- **PDF:** FPDF2
- **Build:** PyInstaller

## Fitur Keamanan

- Anti-duplicate window (mencegah membuka window yang sama)
- Logging aktivitas pengguna
- Filter data berdasarkan kategori (SEMBAKO/TAKTIKAL)

## Kompatibilitas

Aplikasi ini kompatibel dengan:
- Windows 7 (32-bit dan 64-bit)
- Windows 8/8.1
- Windows 10
- Windows 11

## License

© 2024 Koperasi Brimob. All rights reserved.
