"""Mock server MyBest untuk uji offline fastlogin.

Meniru alur elearning.bsi.ac.id:
  GET  /login   -> halaman form berisi _token + captcha SVG teks acak
  POST /login   -> validasi username/password/captcha, redirect ke /dashboard
  GET  /dashboard, /kelas/N -> halaman berisi daftar NIM

Password mock: "mockpass" (atau set env FASTMOCK_PW).
Jalankan: python fastlogin/devmock.py [port]   (default 8765)
"""

import secrets
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote_plus

PASSWORD = "mockpass"
SESSIONS: dict[str, dict] = {}  # sid -> {user, captcha}


def _captcha_svg(captcha: str) -> str:
    chars = "".join(
        f'<text x="{10 + i * 40}" y="30" font-size="26" fill="#333">{c}</text>'
        for i, c in enumerate(captcha)
    )
    return f'<svg width="130" height="40">{chars}</svg>'


def _new_captcha() -> str:
    return "".join(secrets.choice("0123456789ABCDEF") for _ in range(3))


def _login_page(sid: str, msg: str = "") -> bytes:
    captcha = _new_captcha()
    SESSIONS[sid]["captcha"] = captcha
    page = f"""<!doctype html>
<html><head><title>MyBest</title></head><body>
<form action="/login" method="POST">
  <input type="hidden" name="_token" value="{sid}"/>
  <input name="username" placeholder="NIP / NIM"/>
  <input type="password" name="password"/>
  {_captcha_svg(captcha)}
  <input name="captcha_answer" placeholder="Masukkan 3 karakter di atas"/>
  <button type="submit">Masuk</button>
  <p>{msg}</p>
</form></body></html>"""
    return page.encode()


def _dashboard(user: str) -> str:
    return f"""<html><body><h1>Dashboard {user}</h1>
<a href="/kelas/1">Kelas Dasar Manajemen</a>
<a href="/kelas/2">Kelas Logika Algoritma</a>
<p>NIM 15260767 | 15260225 | 15260161</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, code: int = 200, headers: dict | None = None):
        self.send_response(code)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _sid(self):
        for pair in self.headers.get("Cookie", "").split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                if k.strip() == "sid":
                    return v
        return None

    def do_GET(self):
        if self.path in ("/", "/login"):
            sid = secrets.token_urlsafe(16)
            SESSIONS[sid] = {}
            self._send(_login_page(sid), headers={"Set-Cookie": f"sid={sid}; Path=/"})
        elif self.path.startswith("/dashboard") or self.path.startswith("/kelas"):
            sid = self._sid()
            user = SESSIONS.get(sid, {}).get("user")
            if not user:
                self._send(b"", code=302, headers={"Location": "/login"})
                return
            if self.path.startswith("/kelas/1"):
                html = "<html><body>Kelas 1 — NIM 15260767 15260225</body></html>"
            elif self.path.startswith("/kelas/2"):
                html = "<html><body>Kelas 2 — NIM 15260161 15260333</body></html>"
            else:
                html = _dashboard(user)
            self._send(html.encode())
        else:
            self._send(b"404", code=404)

    def do_POST(self):
        if self.path != "/login":
            self._send(b"404", code=404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        fields = dict(
            (k.strip(), unquote_plus(v)) for k, v in
            (p.split("=", 1) for p in body.split("&") if "=" in p)
        )
        sid = fields.get("_token", "")
        entry = SESSIONS.get(sid)
        if not entry or "captcha" not in entry:
            self._send(b"<html>sesi habis, coba lagi</html>".encode(), code=400)
            return

        captcha = entry.pop("captcha", "")
        if captcha != fields.get("captcha_answer", ""):
            SESSIONS[sid]["captcha"] = captcha  # beri kesempatan ulang
            self._send(_login_page(sid, "Captcha salah — coba lagi"), headers={
                "Set-Cookie": f"sid={sid}; Path=/",
            })
            return
        if fields.get("password") != PASSWORD:
            self._send(_login_page(sid, "Password salah"), headers={
                "Set-Cookie": f"sid={sid}; Path=/",
            })
            return

        SESSIONS[sid]["user"] = fields.get("username", "")
        # Mirip aslinya: Laravel redirect ke /dashboard saat sukses
        self._send(b"", code=302, headers={
            "Location": "/dashboard",
            "Set-Cookie": f"sid={sid}; Path=/",
        })

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Mock MyBest: http://127.0.0.1:{port}  (password: {PASSWORD})")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
