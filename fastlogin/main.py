#!/usr/bin/env python3
"""FastLogin MyBest — masuk cepat ke elearning.bsi.ac.id hanya dengan NIM.

Perintah:
    login  <NIM>                Masuk dengan NIM. Password ditanya sekali,
                                lalu disimpan terenkripsi sehingga login
                                berikutnya cukup NIM.
    index  <NIM>                Masuk (otomatis) lalu meramban halaman yang
                                terlihat oleh akun tersebut dan mengindeks
                                seluruh NIM yang ditemukan.
    show                        Tampilkan isi indeks NIM.
    forget <NIM>                Hapus password tersimpan & sesi NIM tersebut.

Opsi umum:
    --base-url URL             Target elearning (default: https://elearning.bsi.ac.id)
    --password PASS            Sediakan password tanpa prompt (tidak tersimpan riwayat shell)
    --manual-captcha           Paksa input captcha manual (fallback bila strategi
                               otomatis gagal karena sistem keamanan berubah)
    --pages N                  Batas halaman diramban untuk `index` (default 40)

Contoh:
    python fastlogin/main.py login 15260767
    python fastlogin/main.py index 15260767 --pages 60
    python fastlogin/main.py login 15260767 --base-url http://127.0.0.1:8765   # uji offline
"""

import argparse
import getpass
import json
import re
import sys
import time
from pathlib import Path

import httpx
from cryptography.fernet import Fernet, InvalidToken

REPO_ROOT = Path(__file__).resolve().parent.parent
STORE_DIR = Path(__file__).resolve().parent / "store"
KEY_FILE = STORE_DIR / "machine.key"
CREDS_FILE = STORE_DIR / "credentials.enc"
SESSIONS_DIR = STORE_DIR / "sessions"
INDEX_FILE = STORE_DIR / "nim_index.json"
CAPTCHA_SNAPSHOT = STORE_DIR / "captcha_terbaru"

LOGIN_PATH = "/login"
DEFAULT_BASE_URL = "https://elearning.bsi.ac.id"
NIM_PATTERN = re.compile(r"\b15\d{6}\b")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}


# ---------------------------------------------------------------------------
# Penyimpanan terenkripsi (Fernet dengan kunci mesin)
# ---------------------------------------------------------------------------

def _load_fernet() -> Fernet:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    if KEY_FILE.exists():
        key = KEY_FILE.read_bytes().strip()
    else:
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
    return Fernet(key)


def load_credentials() -> dict:
    if not CREDS_FILE.exists():
        return {}
    f = _load_fernet()
    try:
        raw = json.loads(CREDS_FILE.read_text())
        return {nim: f.decrypt(tok.encode()).decode() for nim, tok in raw.items()}
    except (InvalidToken, json.JSONDecodeError, OSError):
        return {}


def save_credentials(creds: dict) -> None:
    f = _load_fernet()
    raw = {nim: f.encrypt(pw.encode()).decode() for nim, pw in creds.items()}
    CREDS_FILE.write_text(json.dumps(raw, indent=2))


def delete_credential(nim: str) -> bool:
    creds = load_credentials()
    if nim in creds:
        del creds[nim]
        save_credentials(creds)
        return True
    return False


# ---------------------------------------------------------------------------
# Strategi captcha (berlapis — tetap masuk walau sistem keamanan berubah)
# ---------------------------------------------------------------------------

def solve_captcha_auto(html: str) -> str | None:
    """Baca jawaban captcha dari HTML dengan beberapa strategi berurutan."""
    # Strategi 1: captcha SVG text — karakter terrender di elemen <text>
    svg_texts = re.findall(r"<text[^>]*>([^<]+)</text>", html)
    if svg_texts:
        answer = "".join(t.strip() for t in svg_texts)
        if answer and not answer.isspace():
            return answer

    # Strategi 2: pola matematika klasik ("12 + 5")
    m = re.search(r"(\d+)\s*\+\s*(\d+)", html)
    if m:
        return str(int(m.group(1)) + int(m.group(2)))

    # Strategi 3: kode dalam atribut (data-captcha, alt, aria-label)
    m = re.search(r'(?:data-captcha|alt|aria-label)\s*=\s*["\']([0-9A-Za-z]{3,6})["\']', html)
    if m:
        return m.group(1)

    return None


def save_captcha_snapshot(html: str) -> Path | None:
    """Simpan captcha (SVG utuh atau URL gambar) agar bisa dibuka manual."""
    svg = re.search(r"<svg[\s\S]*?</svg>", html)
    if svg:
        path = CAPTCHA_SNAPSHOT.with_suffix(".svg")
        path.write_text(svg.group(0))
        return path
    img = re.search(r'<img[^>]+src\s*=\s*["\']([^"\']*(?:captcha|keamanan)[^"\']*)["\']', html, re.I)
    if img:
        path = CAPTCHA_SNAPSHOT.with_suffix(".url.txt")
        path.write_text(img.group(1))
        return path
    return None


# ---------------------------------------------------------------------------
# Login inti
# ---------------------------------------------------------------------------

def new_client(base_url: str) -> httpx.Client:
    return httpx.Client(
        base_url=base_url, headers={"User-Agent": HEADERS["User-Agent"]},
        follow_redirects=True, timeout=30.0,
    )


def try_login(nim: str, password: str, base_url: str,
              manual_captcha: bool) -> tuple[bool, str | None, httpx.Client]:
    """Satu percobaan login: GET sekali, baca captcha, POST — tanpa GET ulang
    (captcha termasuk _token kedaluwarsa bila halaman dimuat ulang)."""
    client = new_client(base_url)
    r1 = client.get(LOGIN_PATH)

    captcha_answer = None
    if not manual_captcha:
        captcha_answer = solve_captcha_auto(r1.text)

    if captcha_answer is None:
        snapshot = save_captcha_snapshot(r1.text)
        print("[!] Captcha tidak terbaca otomatis — mode manual.")
        if snapshot:
            print(f"    Buka berkas ini untuk melihat kodenya: {snapshot}")
        captcha_answer = input("    Ketik kode keamanan: ").strip()

    return _post_login(client, r1.text, nim, password, captcha_answer)


def _post_login(client: httpx.Client, html: str, nim: str, password: str,
                captcha_answer: str) -> tuple[bool, str | None, httpx.Client]:
    """Kirim form login dari HTML yang sudah diambil (satu GET per percobaan)."""
    # Deteksi form secara dinamik agar tetap bekerja saat markup berubah
    m = re.search(r"<form[^>]*>[\s\S]*?</form>", html)
    form_html = m.group(0) if m else html

    action = ""
    ma = re.search(r'action\s*=\s*["\']([^"\']*)["\']', form_html)
    if ma:
        action = ma.group(1)

    body: dict[str, str] = {}
    for tag in re.finditer(r"<input\b[^>]*>", form_html):
        tag_html = tag.group(0)
        name = re.search(r'name\s*=\s*["\']([^"\']+)["\']', tag_html)
        if not name:
            continue
        val = re.search(r'value\s*=\s*["\']([^"\']*)["\']', tag_html)
        body[name.group(1)] = val.group(1) if val else ""

    user_key = next((k for k in body if re.search(r"user|nim|email|login", k, re.I)), None)
    pass_key = next((k for k in body if re.search(r"pass", k, re.I)), None)
    captcha_key = next((k for k in body if re.search(r"captcha|keamanan|security", k, re.I)), None)
    if user_key:
        body[user_key] = nim
    if pass_key:
        body[pass_key] = password
    if captcha_key:
        body[captcha_key] = captcha_answer

    resp = client.post(action or LOGIN_PATH, data=body)
    if "dashboard" in str(resp.url) or "/user" in str(resp.url):
        return True, None, client

    reason = "Kredensial atau captcha salah"
    if "captcha" in resp.text.lower() and captcha_answer:
        reason = "Kemungkinan captcha salah/jatuh tempo"
    return False, reason, client


def save_session(nim: str, cookies: dict) -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    (SESSIONS_DIR / f"{nim}.json").write_text(
        json.dumps({"cookies": cookies, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")})
    )


def login(nim: str, password: str | None, base_url: str, manual_captcha: bool) -> bool:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sessions_file = SESSIONS_DIR / f"{nim}.json"

    # 1) Sesi tersimpan — masuk tanpa password sama sekali
    if sessions_file.exists() and not manual_captcha:
        try:
            session_data = json.loads(sessions_file.read_text())
            client = new_client(base_url)
            for name, value in session_data["cookies"].items():
                client.cookies.set(name, value)
            probe = client.get("/dashboard")
            if "login" not in str(probe.url) and probe.status_code == 200:
                print(f"[✓] {nim}: masuk via sesi tersimpan (tanpa password).")
                return True
        except (OSError, KeyError, httpx.HTTPError):
            pass  # sesi kedaluwarsa — lanjut ke password tersimpan

    # 2) Password tersimpan, atau tanya sekali lalu simpan terenkripsi
    creds = load_credentials()
    first_time = nim not in creds
    if password is None:
        password = creds.get(nim)
        if password is None:
            password = getpass.getpass(f"Password MyBest untuk {nim}: ")
        creds[nim] = password
        save_credentials(creds)
    else:
        creds[nim] = password
        save_credentials(creds)

    # 3) Percobaan: 2x otomatis, lalu 1x paksa manual (fallback anti-sistem-baru)
    attempts = [(False, "otomatis"), (False, "otomatis"), (True, "manual")] \
        if not manual_captcha else [(True, "manual")]
    for manual, label in attempts:
        ok, reason, client = try_login(nim, password, base_url, manual_captcha=manual)
        if ok:
            cookies = {c.name: c.value for c in client.cookies.jar}
            sessions_file.write_text(
                json.dumps({"cookies": cookies,
                            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")})
            )
            client.close()
            print(f"[✓] {nim}: berhasil masuk (mode {label}). Sesi tersimpan.")
            return True
        print(f"[!] Percobaan ({label}) gagal: {reason}")
        client.close()
    return False


# ---------------------------------------------------------------------------
# Indexing NIM
# ---------------------------------------------------------------------------

def index_nims(nim: str, base_url: str, max_pages: int) -> set:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sessions_file = SESSIONS_DIR / f"{nim}.json"
    if not sessions_file.exists():
        print(f"[!] Belum ada sesi untuk {nim}. Jalankan: login {nim} dulu.")
        return set()

    cookies = json.loads(sessions_file.read_text())["cookies"]
    client = new_client(base_url)
    for name, value in cookies.items():
        client.cookies.set(name, value)

    # BFS ramban halaman same-origin
    seen, found = set(), set()
    queue = ["/dashboard"]
    while queue and len(seen) < max_pages:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        try:
            resp = client.get(path)
        except httpx.HTTPError:
            continue
        html = resp.text
        for m in NIM_PATTERN.finditer(html):
            found.add(m.group(0))
        for href in re.findall(r'href\s*=\s*["\']([^"\'#]+)["\']', html):
            clean = href.strip()
            if clean.startswith("//"):
                continue
            if clean.startswith("http"):
                if base_url not in clean:
                    continue
                clean = clean.replace(base_url, "")
            if clean.startswith("/"):
                queue.append(clean)
        print(f"    diramban: {path}  ({len(found)} NIM kumulatif)")

    index = json.loads(INDEX_FILE.read_text()) if INDEX_FILE.exists() else {"nims": {}}
    today = time.strftime("%Y-%m-%d %H:%M:%S")
    for n in sorted(found):
        entry = index["nims"].get(n, {"sources": []})
        entry["last_seen"] = today
        index["nims"][n] = entry
    INDEX_FILE.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    return found


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="fastlogin", description="Masuk cepat ke MyBest hanya dengan NIM.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_login = sub.add_parser("login", help="Masuk dengan NIM (password sekali saja)")
    p_login.add_argument("nim")
    p_login.add_argument("--password", help="Sediakan password tanpa prompt")
    p_login.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p_login.add_argument("--manual-captcha", action="store_true",
                         help="Paksa input captcha manual")

    p_index = sub.add_parser("index", help="Indeks semua NIM yang terlihat akun")
    p_index.add_argument("nim")
    p_index.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p_index.add_argument("--pages", type=int, default=40)

    sub.add_parser("show", help="Tampilkan indeks NIM")

    p_forget = sub.add_parser("forget", help="Hapus password & sesi NIM")
    p_forget.add_argument("nim")

    args = ap.parse_args()

    if args.cmd == "login":
        return 0 if login(args.nim, args.password, args.base_url,
                          args.manual_captcha) else 1
    if args.cmd == "index":
        found = index_nims(args.nim, args.base_url, args.pages)
        print(f"\n[i] {len(found)} NIM baru/tetap terindeks: {sorted(found)}")
        print(f"    Tersimpan di {INDEX_FILE}")
        return 0
    if args.cmd == "show":
        if INDEX_FILE.exists():
            nims = json.loads(INDEX_FILE.read_text())["nims"]
            for n, meta in sorted(nims.items()):
                print(f"  {n}  (terakhir terlihat: {meta.get('last_seen', '?')})")
            print(f"\n[i] Total {len(nims)} NIM.")
        else:
            print("[i] Indeks masih kosong. Jalankan: index <NIM>")
        return 0
    if args.cmd == "forget":
        ok = delete_credential(args.nim)
        f = SESSIONS_DIR / f"{args.nim}.json"
        if f.exists():
            f.unlink()
        print(f"[{'✓' if ok else 'i'}] Password {args.nim} "
              f"{'dihapus' if ok else 'memang tidak tersimpan'}.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
