# Video Clipper

Situs sederhana untuk mengambil link/info video dari YouTube, TikTok, dan
Instagram, memakai library open-source `yt-dlp` di backend.

## Struktur
```
video-clipper/
├── backend/          -> API Python (Flask) yang melakukan ekstraksi video
│   ├── app.py
│   ├── requirements.txt
│   └── render.yaml   -> config siap pakai untuk deploy ke Render
└── frontend/
    └── index.html    -> halaman web yang dipakai pengguna
```

## 1. Menjalankan di komputer sendiri (untuk dicoba dulu)
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend akan jalan di `http://localhost:5000`. Buka `frontend/index.html`
langsung di browser — variabel `BACKEND_URL` di dalam file itu sudah
diarahkan ke `http://localhost:5000`.

## 2. Deploy backend (server yang jalan terus)
Karena backend butuh server Python yang aktif (bukan cuma file statis),
pakai salah satu dari:
- **Render.com** (gratis untuk trafik kecil): buat "New Web Service", hubungkan
  ke repo GitHub kamu yang berisi folder `backend/`, Render akan otomatis
  membaca `render.yaml`.
- **Railway.app** atau **Fly.io**: caranya mirip, upload folder `backend/`
  sebagai satu service Python.

Setelah deploy, kamu akan dapat URL publik, misalnya:
`https://video-clipper-backend.onrender.com`

## 3. Deploy frontend (bisa 100% gratis)
1. Buka `frontend/index.html`, ganti baris:
   ```js
   const BACKEND_URL = "http://localhost:5000";
   ```
   jadi URL backend yang sudah online, misalnya:
   ```js
   const BACKEND_URL = "https://video-clipper-backend.onrender.com";
   ```
2. Upload folder `frontend/` ke:
   - **Netlify** (drag & drop folder, langsung jadi link),
   - **Vercel**, atau
   - **GitHub Pages**.

Setelah ini kamu sudah punya link web sendiri yang bisa dibagikan.

## Tentang webhook
- `WEBHOOK_URL` (environment variable di backend): kalau diisi, setiap kali
  ada video berhasil/gagal diekstrak, backend akan mengirim POST request ke
  URL itu (misalnya webhook Discord, Slack, Zapier, atau server kamu sendiri).
- Endpoint `/webhook` di `app.py`: ini kebalikannya — tempat untuk MENERIMA
  data dari sistem luar. Isi logic-nya sesuai kebutuhanmu (baris `TODO` di
  dalam kode).

## Batasan yang perlu kamu tahu
- `yt-dlp` bukan API resmi — ia membaca halaman video seperti browser biasa.
  Instagram dan TikTok termasuk platform yang paling sering mengubah
  struktur situsnya, jadi extractor bisa berhenti bekerja sewaktu-waktu dan
  butuh update `yt-dlp` (`pip install -U yt-dlp`) secara berkala.
- Video privat/dibatasi region biasanya perlu file `cookies.txt` dari akun
  yang sudah login (sudah disiapkan tempatnya di `app.py`, tinggal
  diaktifkan).
- Mengambil dan mengunduh ulang konten milik orang lain tanpa izin bisa
  melanggar hak cipta dan ketentuan layanan platform terkait — tanggung
  jawab pemakaiannya ada di pihak yang menjalankan situs ini.
