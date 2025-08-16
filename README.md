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

## 📂 Struktur Kode `Project1.py`

File ini dibagi menjadi beberapa bagian logis:

### 1. Imports
Bagian ini mengimpor semua library dan modul yang diperlukan oleh aplikasi, seperti `Flask`, `Selenium`, `BeautifulSoup`, dan `fitz`.

### 2. Inisialisasi Aplikasi Flask
Baris `app = Flask(__name__)` dan `app.secret_key` digunakan untuk membuat instance aplikasi web dan mengonfigurasi kunci rahasia untuk manajemen sesi (session).

### 3. Fungsi-fungsi Helper
Ini adalah fungsi-fungsi inti yang menangani logika scraping:
* `get_item_page_links()`: Mengambil semua link halaman detail skripsi dari halaman daftar subjek.
* `get_pdfs_from_item_page()`: Mengambil semua link file `.pdf` dari satu halaman detail skripsi.
* `read_pdf_from_url()`: Mengunduh dan mengekstrak seluruh teks dari sebuah file PDF.

### 4. Rute-rute Aplikasi (Endpoints)
Ini adalah bagian yang mendefinisikan halaman-halaman dan fungsionalitas API dari aplikasi web:
* `@app.route("/")`: Menampilkan halaman utama (`Project1.html`) tempat pengguna memasukkan kriteria pencarian.
* `@app.route("/manual")`: Menampilkan halaman panduan (`manual.html`).
* `@app.route("/login")`: Menangani proses login. Rute ini menerima username dan password, lalu menggunakan Selenium untuk melakukan login otomatis di latar belakang dan menyimpan *cookies* sesi.
* `@app.route("/scrape")`: Endpoint utama yang memulai proses scraping. Rute ini menerima data dari form, menjalankan fungsi-fungsi helper, dan mengirimkan hasilnya secara *real-time* ke browser.
* Rute lainnya seperti `/logout`, `/check-status`, dan `/data-jurusan` berfungsi sebagai pendukung untuk manajemen sesi dan pengambilan data dinamis.

---

## ⚙️ Panduan Instalasi & Menjalankan (Lokal)

### Prasyarat
* Python 3.10+
* Git
* Browser Google Chrome

### Langkah-langkah
1.  **Clone Repositori:**
    ```bash
    git clone [URL_REPOSITORI_ANDA]
    cd [NAMA_FOLDER_PROYEK]
    ```

2.  **Instal Semua Library:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Jalankan Aplikasi:**
    ```bash
    python Project1.py
    ```
    Buka browser dan akses **http://127.0.0.1:5000**.
