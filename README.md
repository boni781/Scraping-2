# Dokumentasi Proyek Aplikasi Scraping

File ini menjelaskan struktur dan fungsionalitas dari `Project1.py`, sebuah aplikasi web berbasis Flask yang dirancang untuk melakukan scraping data dari repository UPN "Veteran" Jawa Timur.

---

##  Deskripsi Proyek

Aplikasi ini menyediakan antarmuka web yang memungkinkan pengguna untuk mencari kata kunci tertentu di dalam dokumen-dokumen PDF yang ada di repository. Fitur utamanya adalah kemampuan untuk login secara otomatis menggunakan Selenium, sehingga dapat mengakses dokumen yang bersifat terbatas (*restricted*).

---

## 🛠️ Teknologi yang Digunakan

* **Backend:** Flask
* **Web Scraping:** BeautifulSoup & Requests
* **Automasi Browser (Login):** Selenium
* **Pembacaan PDF:** PyMuPDF (fitz)
* **Deployment:** Gunicorn (untuk server WSGI)

---

# Proyek Scraping Repository UPN Jatim (Panduan Pemula)

Selamat datang! Ini adalah panduan lengkap untuk menjalankan aplikasi web scraping di komputer Anda. Aplikasi ini dibuat untuk mencari data di dalam dokumen pada repository UPN "Veteran" Jawa Timur.

---

## ✨ Fitur Utama
* **Login Otomatis:** Bisa masuk ke sistem repository untuk mengakses dokumen yang dilindungi.
* **Dua Mode Pencarian:**
    1.  **Mode Daftar (List):** Mencari dari banyak dokumen berdasarkan jurusan dan tahun.
    2.  **Mode Detail:** Mencari di satu dokumen spesifik.
* **Hasil Real-time:** Proses pencarian ditampilkan secara langsung di browser.
* **Pembacaan PDF:** Mampu membaca isi dokumen PDF untuk menemukan kata kunci.

---

## ✅ Persiapan Awal

Sebelum mulai, pastikan dua hal ini sudah ada di komputer Anda:

1.  **Python**: Minimal versi 3.10. Jika belum punya, unduh dari [python.org](https://www.python.org/downloads/). Saat instalasi, **centang kotak "Add Python to PATH"**.
2.  **Browser Google Chrome**: Aplikasi ini akan mengontrol Google Chrome, jadi pastikan browsernya sudah terinstal.

---

## ⚙️ Instalasi (Cara Mudah via Download ZIP)

Ikuti langkah-langkah ini untuk menjalankan aplikasi.

### Langkah 1: Unduh dan Ekstrak Proyek
1.  Buka halaman utama repositori ini di GitHub.
2.  Klik tombol hijau **`< > Code`**.
3.  Pilih **`Download ZIP`**. 
4.  Setelah selesai diunduh, cari file `.zip` tersebut di komputer Anda (biasanya di folder "Downloads").
5.  **Klik kanan** pada file zip lalu pilih **`Extract All...`** atau **`Ekstrak Semua...`**. Simpan hasil ekstraknya di lokasi yang mudah Anda ingat (misalnya di Desktop).

### Langkah 2: Buka Terminal di dalam Folder Proyek
Sekarang, Anda perlu membuka terminal (Command Prompt atau PowerShell) tepat di dalam folder yang baru saja Anda ekstrak.

* **Cara Termudah (Windows):** Buka folder proyek, **klik kanan** pada area kosong di dalam folder, lalu pilih **`Open in Terminal`** atau **`Buka di Terminal`**.

* **Cara Alternatif (`cd`):** Buka terminal secara manual, lalu ketik `cd` diikuti dengan path ke folder proyek Anda. Contoh:
    ```bash
    cd C:\Users\NamaAnda\Desktop\scraping-offline-main
    ```

### Langkah 3: Instal Semua *Library*
Terakhir, jalankan perintah ini untuk menginstal semua *library* yang dibutuhkan (seperti Flask, Selenium, dll.) secara otomatis.

```bash
pip install -r requirements.txt
```

4.  **Jalankan Aplikasi:**
    ```bash
    python Project1.py
    ```
    Buka browser dan akses **http://127.0.0.1:5000**.

