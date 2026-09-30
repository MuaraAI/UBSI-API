import hashlib
import random
from typing import Optional
from app.config import settings

def normalize_proxy(raw: str) -> Optional[str]:
    """
    Normalisasi format proxy menjadi URL standar yang dapat dibaca httpx & curl_cffi:
    - "http://ip:port" -> tetap
    - "socks5://ip:port" -> tetap
    - "ip:port" -> "http://ip:port"
    - "ip:port:user:pass" -> "http://user:pass@ip:port"
    - "user:pass@ip:port" -> "http://user:pass@ip:port"
    """
    if not raw:
        return None
    cleaned = raw.strip()
    if not cleaned:
        return None

    if "://" in cleaned:
        return cleaned

    parts = cleaned.split(":")
    if len(parts) == 4:
        # Format ip:port:user:pass
        ip, port, user, pwd = parts
        return f"http://{user}:{pwd}@{ip}:{port}"

    return f"http://{cleaned}"

def get_proxy(seed: Optional[str] = None) -> Optional[str]:
    """
    Kembalikan proxy URL yang telah dinormalisasi.
    - Jika seed (misal NIM) diberikan: Gunakan Sticky Proxy konsisten untuk mahasiswa tersebut.
    - Jika seed None: Rotasi acak dari SCRAPER_PROXY_POOL atau fallback ke SCRAPER_PROXY tunggal.
    """
    pool_raw = settings.SCRAPER_PROXY_POOL.strip()
    if pool_raw:
        pool = [normalize_proxy(p) for p in pool_raw.split(",") if normalize_proxy(p)]
        if pool:
            if seed:
                # Deterministik sha256 hash agar sticky konsisten antar request/sesi NIM
                h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16)
                return pool[h % len(pool)]
            return random.choice(pool)

    single_raw = settings.SCRAPER_PROXY.strip()
    if single_raw:
        return normalize_proxy(single_raw)

    return None
