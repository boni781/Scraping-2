# =================================================================
# 📂 IMPORTS
# =================================================================
import io
import json
import re
import time
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from flask import (Flask, request, render_template, jsonify, Response, 
                   stream_with_context, render_template_string, url_for, session)

# --- Import untuk Selenium ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

# =================================================================
# ⚙️ INISIALISASI APLIKASI FLASK
# =================================================================
app = Flask(__name__)
app.secret_key = 'kunci-rahasia-anda-yang-sangat-sulit-ditebak'

# =================================================================
# 📚 TEMPLATE (TIDAK DIUBAH SESUAI PERMINTAAN)
# =================================================================
STREAM_LAYOUT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Scraping Results...</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <style>
        .main-content-wrapper { display: flex; gap: 30px; align-items: flex-start; }
        .results-panel { flex: 2; }
        .log-panel { flex: 1; }
        #log-container { height: 450px !important; overflow-y: auto !important; word-break: break-all; }
        .result-item { font-size: 14px; line-height: 1.5; }
        .result-item a { word-break: break-all; }
        .result-item ul { list-style-type: none; padding-left: 0; margin-top: 10px; }
        .result-item li { padding-left: 1.5em; text-indent: -1.5em; margin-bottom: 8px; }
        .result-item li::before { content: '🔗'; margin-right: 8px; }
        .section h2::before { display: inline-block; margin-right: 10px; vertical-align: middle; }
        .results-panel h2::before { content: '📋'; }
        .log-panel h2::before { content: '⚙️'; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>Scraping Results</h1></div>
        <div class="main-content-wrapper">
            <div class="results-panel section">
                <h2>Hasil Ditemukan</h2>
                <div class="section-content" id="results-container"></div>
            </div>
            <div class="log-panel section">
                <h2>Log Proses</h2>
                <div class="section-content"><div id="log-container"></div></div>
            </div>
        </div>
        <p class="finished" id="status-finished" style="display:none;">✅ Proses Selesai.</p>
        <div class="footer-nav"><a href="/">Kembali ke Pencarian</a></div>
    </div>
    <script>
        const logContainer = document.getElementById('log-container');
        const resultsContainer = document.getElementById('results-container');
        function clearSavedResults() { localStorage.removeItem('savedResultsHTML'); localStorage.removeItem('savedLogsHTML'); resultsContainer.innerHTML = '<p id="no-results-yet">Belum ada hasil...</p>'; logContainer.innerHTML = ''; }
        function loadResultsFromStorage() { const savedResults = localStorage.getItem('savedResultsHTML'); const savedLogs = localStorage.getItem('savedLogsHTML'); if (savedResults) { resultsContainer.innerHTML = savedResults; } else { resultsContainer.innerHTML = '<p id="no-results-yet">Belum ada hasil...</p>'; } if (savedLogs) { logContainer.innerHTML = savedLogs; logContainer.scrollTop = logContainer.scrollHeight; } }
        function addLog(htmlContent) { logContainer.insertAdjacentHTML('beforeend', htmlContent); logContainer.scrollTop = logContainer.scrollHeight; localStorage.setItem('savedLogsHTML', logContainer.innerHTML); }
        function addResult(htmlContent) { const noResultsMessage = document.getElementById('no-results-yet'); if (noResultsMessage) { noResultsMessage.remove(); } resultsContainer.insertAdjacentHTML('beforeend', htmlContent); localStorage.setItem('savedResultsHTML', resultsContainer.innerHTML); }
        function markAsFinished() { document.getElementById('status-finished').style.display = 'block'; }
        document.addEventListener('DOMContentLoaded', function() { loadResultsFromStorage(); });
    </script>
</body>
</html>
"""
RESULT_SNIPPET_HTML = """
<div class="result-item">
  <h3>🎉 Ditemukan di: <a href="{{ result.item_page }}" target="_blank">{{ result.item_page }}</a></h3>
  <ul>
    {% for pdf in result.pdfs %}
      <li><a href="{{ pdf.pdf_url }}" target="_blank">{{ pdf.pdf_url }}</a> (Ditemukan: <strong>{{ pdf.count }}</strong> kali)</li>
    {% endfor %}
  </ul>
</div>
"""
LOG_SNIPPET_HTML = "<p>{{ message }}</p>"
ERROR_SNIPPET_HTML = '<p class="log-error">❌ {{ message }}</p>'

# =================================================================
# 🛠️ FUNGSI-FUNGSI HELPER (DIPERBARUI)
# =================================================================

def get_item_page_links(url, anchor_name=None, authenticated_session=None):
    client = authenticated_session or requests
    try:
        response = client.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        search_scope = soup
        if anchor_name:
            anchor = soup.find(id=anchor_name) or soup.find("a", {"name": anchor_name})
            if anchor: search_scope = anchor.find_all_next("a", href=True)
            else: search_scope = soup.find_all("a", href=True)
        else:
            search_scope = soup.find_all("a", href=True)
                
        item_links = [] 
        for a in search_scope:
            if not hasattr(a, 'get'): continue
            href = a.get("href", "")
            full_url = requests.compat.urljoin(url, href)
            if re.search(r"/\d{3,6}/$", full_url) and not re.search(r"\.\w{3,4}$", full_url, re.IGNORECASE):
                if full_url not in item_links:
                    item_links.append(full_url)
        return item_links
    except requests.exceptions.RequestException:
        return []

def get_pdfs_from_item_page(item_url, authenticated_session=None):
    client = authenticated_session or requests
    try:
        response = client.get(item_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        pdf_links = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if re.search(r"\.pdf(\?|$)", href, re.IGNORECASE) and "lightbox" not in href:
                pdf_links.add(requests.compat.urljoin(item_url, href))
        return list(pdf_links)
    except requests.exceptions.RequestException:
        return []

def read_pdf_from_url(pdf_url, authenticated_session=None):
    client = authenticated_session or requests
    try:
        response = client.get(pdf_url, timeout=60)
        response.raise_for_status()
        if 'text/html' in response.headers.get('Content-Type', ''): return ""
        with fitz.open(stream=io.BytesIO(response.content), filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
    except Exception:
        return ""

# =================================================================
# 🌐 RUTE-RUTE APLIKASI
# =================================================================
@app.route("/")
def index(): return render_template("Project1.html")

@app.route('/manual')
def manual(): return render_template('manual.html')

@app.route('/data-jurusan')
def data_jurusan(): 
    try:
        with open("jurusan_upn.json", encoding="utf-8") as f: data = json.load(f)
        return jsonify(data)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/data-anchor')
def data_anchor():
    try:
        with open("anchors.json", encoding="utf-8") as f: data = json.load(f)
        return jsonify(data)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    login_url = 'https://repository.upnjatim.ac.id/cgi/users/login'

    # --- PERUBAHAN DI SINI ---
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Menentukan path secara manual untuk driver dan browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Hapus bagian path manual, biarkan Selenium mencari otomatis di PATH
    driver = webdriver.Chrome(options=options)
    # --- AKHIR PERUBAHAN ---

    try:
        driver.get(login_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_username"))).send_keys(username)
        driver.find_element(By.ID, "login_password").send_keys(password)
        driver.find_element(By.NAME, "_action_login").click()
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Manage deposits')]")))
        
        session['logged_in'] = True
        session['username'] = username
        
        cookies = driver.get_cookies()
        with open('credentials.json', 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
        
        return jsonify({'success': True, 'message': f'Login sebagai {username} berhasil! Cookie disimpan.'})

    except Exception as e:
        session.clear()
        driver.save_screenshot('debug_selenium_login_failed.png')
        error_message = f"Login gagal. Error: {str(e)}" # Memberikan error yang lebih spesifik
        return jsonify({'success': False, 'message': error_message})
    finally:
        driver.quit()

@app.route('/logout')
def logout():
    session.clear()
    if 'credentials.json' in __import__('os').listdir():
        __import__('os').remove('credentials.json')
    return jsonify({'success': True, 'message': 'Anda telah logout.'})

@app.route('/check-status')
def check_status():
    if session.get('logged_in'):
        return jsonify({'logged_in': True, 'username': session.get('username')})
    return jsonify({'logged_in': False})

@app.route('/hasil')
def hasil(): return render_template_string(STREAM_LAYOUT_HTML)

@app.route("/scrape", methods=["POST"])
def scrape():
    form_data = request.form
    url_input = form_data.get("url", "")
    selected_jurusan_name = form_data.get("jurusan", "")
    keyword = form_data.get("keyword", "").lower()
    mode = form_data.get("scrape_mode", "list")
    start_index = form_data.get("start_index", 0, type=int)
    limit = form_data.get("limit", 3, type=int)
    anchor_name = form_data.get("anchor_name", "").strip()

    target_url = ""
    if url_input: target_url = url_input
    elif selected_jurusan_name:
        try:
            with open("jurusan_upn.json", encoding="utf-8") as f:
                jurusan_data = json.load(f)
            target_url = jurusan_data.get(selected_jurusan_name)
        except Exception: pass
            
    def generate_results():
        yield render_template_string(STREAM_LAYOUT_HTML)
        yield "<script>clearSavedResults();</script>\n"

        def stream_event(func, template, context):
            html = render_template_string(template, **context)
            yield f"<script>{func}({json.dumps(html)});</script>\n"
        def stream_log(msg, is_err=False):
            yield from stream_event("addLog", ERROR_SNIPPET_HTML if is_err else LOG_SNIPPET_HTML, {"message": msg})
        def stream_result(data):
            yield from stream_event("addResult", RESULT_SNIPPET_HTML, {"result": data})

        authenticated_session = None
        if session.get('logged_in'):
            yield from stream_log("Status: Login terdeteksi. Memuat cookie sesi...")
            try:
                with open('credentials.json', 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                
                authenticated_session = requests.Session()
                for cookie in cookies:
                    authenticated_session.cookies.set(cookie['name'], cookie['value'])
                
                authenticated_session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                yield from stream_log("✅ Berhasil membuat sesi terotentikasi untuk scraping.")
            except Exception:
                yield from stream_log("❌ Gagal memuat cookie. Melanjutkan tanpa login.", is_err=True)
                authenticated_session = None
        else:
            yield from stream_log("Status: Tidak login. Scraping akan dilakukan sebagai tamu.")

        if not target_url or not keyword:
            yield from stream_log("Error: URL/Jurusan atau Kata Kunci tidak valid.", is_err=True)
            yield "<script>markAsFinished();</script>\n"
            return
        
        if mode == "detail":
            yield from stream_log(f"Mode Detail: Memeriksa {target_url}...")
            pdf_links = get_pdfs_from_item_page(target_url, authenticated_session=authenticated_session)
            if not pdf_links: yield from stream_log("Tidak ada PDF ditemukan.", is_err=True)
            else:
                valid_pdfs = [p for url in pdf_links if (text := read_pdf_from_url(url, authenticated_session=authenticated_session)) and (count := text.lower().count(keyword)) > 0 and (p := {"pdf_url": url, "count": count})]
                if valid_pdfs: yield from stream_result({"item_page": target_url, "pdfs": valid_pdfs})
                else: yield from stream_log(f"Kata kunci '{keyword}' tidak ditemukan.")
        else:
            yield from stream_log(f"Mode Daftar: Mengambil link dari {target_url} (Anchor: {anchor_name or 'Tidak ada'})...")
            item_pages = get_item_page_links(target_url, anchor_name, authenticated_session=authenticated_session)
            total = len(item_pages)
            if not item_pages: yield from stream_log("Tidak dapat mengambil daftar item.", is_err=True)
            yield from stream_log(f"Ditemukan {total} item. Memproses dari indeks {start_index} (limit {limit}).")
            
            found_any = False
            for i, item_url in enumerate(item_pages[start_index : start_index + limit]):
                yield from stream_log(f"[{start_index + i + 1}/{total}] Memeriksa: {item_url}")
                pdf_links = get_pdfs_from_item_page(item_url, authenticated_session=authenticated_session)
                if not pdf_links: continue
                
                valid_pdfs = [p for url in pdf_links if (text := read_pdf_from_url(url, authenticated_session=authenticated_session)) and (count := text.lower().count(keyword)) > 0 and (p := {"pdf_url": url, "count": count})]
                if valid_pdfs:
                    found_any = True
                    yield from stream_result({"item_page": item_url, "pdfs": valid_pdfs})
            
            if not found_any: yield from stream_log("Tidak ada hasil ditemukan pada rentang yang diperiksa.")

        yield "<script>markAsFinished();</script>\n"

    return Response(stream_with_context(generate_results()), mimetype='text/html')

# =================================================================
# 🚀 MENJALANKAN APLIKASI
# =================================================================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)