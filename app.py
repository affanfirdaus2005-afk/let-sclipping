"""
Backend sederhana untuk 'Video Clipper'.
Menggunakan yt-dlp (open source) untuk mengambil info & link video
dari YouTube, TikTok, Instagram, dsb.

Catatan penting:
- yt-dlp tidak resmi didukung oleh platform-platform tersebut.
- Instagram & TikTok sering butuh cookie login untuk konten tertentu,
  dan extractor-nya bisa saja berhenti bekerja saat platform berubah.
- Jangan pakai untuk mengunduh konten berhak cipta tanpa izin pemiliknya.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)  # supaya frontend di domain lain bisa memanggil API ini

# URL webhook eksternal (opsional). Isi lewat environment variable
# kalau kamu mau setiap hasil ekstraksi dikirim notifikasi ke sistem lain
# (misal ke Discord, Slack, Zapier, atau server kamu sendiri).
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").strip()


def send_webhook(payload: dict):
    """Kirim event ke WEBHOOK_URL kalau sudah diset. Gagal kirim tidak boleh
    menghentikan proses utama, jadi errornya cuma dicetak ke log."""
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:  # noqa: BLE001
        print(f"[webhook] gagal mengirim: {e}")


@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "video-clipper-backend"})


@app.route("/api/extract", methods=["POST"])
def extract():
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "URL tidak boleh kosong"}), 400

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        # Kalau nanti butuh login (misal video Instagram privat/TikTok
        # yang dibatasi region), taruh file cookies.txt di folder ini
        # dan aktifkan baris di bawah:
        # "cookiefile": "cookies.txt",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:  # noqa: BLE001
        send_webhook({"event": "extract_failed", "url": url, "error": str(e)})
        return jsonify({"error": f"Gagal mengambil video: {e}"}), 422

    formats = [
        {
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "resolution": f.get("resolution") or f.get("height"),
            "filesize": f.get("filesize") or f.get("filesize_approx"),
            "url": f.get("url"),
        }
        for f in info.get("formats", [])
        if f.get("url")
    ]

    result = {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "platform": info.get("extractor_key"),
        # ambil beberapa format kualitas terbaik terakhir dari daftar
        "formats": formats[-8:] if formats else [],
        "direct_url": info.get("url"),  # fallback kalau formats kosong
    }

    send_webhook({"event": "extract_success", "url": url, "title": result["title"], "platform": result["platform"]})
    return jsonify(result)


@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    """
    Endpoint untuk MENERIMA webhook dari luar (kebalikan dari fungsi di atas).
    Contoh pemakaian: sistem lain (misal bot Telegram/Discord) mengirim
    request ke sini untuk memicu proses tambahan di server kamu.
    Ganti logic di dalamnya sesuai kebutuhanmu.
    """
    payload = request.get_json(force=True, silent=True) or {}
    print("[webhook] diterima:", payload)
    # TODO: taruh logic kamu sendiri di sini, misal simpan ke database
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
