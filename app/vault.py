import os
import base64
import hashlib
from typing import Optional
import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings
from app.cache import cache

class VaultDecryptionError(Exception):
    """Raised when vault ciphertext is invalid, corrupted, or fails authentication tag verification."""
    pass

def _parse_key(key_input: str) -> bytes:
    """Parse encryption key from a 64-char hex string or a 32-byte UTF-8 string."""
    if len(key_input) == 64:
        try:
            return bytes.fromhex(key_input)
        except ValueError:
            pass
    b = key_input.encode("utf-8")
    if len(b) == 32:
        return b
    raise ValueError("VAULT_ENCRYPTION_KEY must be exactly 32 bytes (or a 64-character hex string)")

def encrypt_credential(plain_text: str, key_input: str) -> str:
    """
    Encrypt plaintext string using AES-256-GCM.
    Returns: {iv_b64}.{ciphertext_b64}
    """
    key_bytes = _parse_key(key_input)
    aesgcm = AESGCM(key_bytes)
    iv = os.urandom(12)
    ciphertext = aesgcm.encrypt(iv, plain_text.encode("utf-8"), None)

    iv_b64 = base64.urlsafe_b64encode(iv).decode("utf-8").rstrip("=")
    ct_b64 = base64.urlsafe_b64encode(ciphertext).decode("utf-8").rstrip("=")
    return f"{iv_b64}.{ct_b64}"

def decrypt_credential(cipher_str: str, key_input: str) -> str:
    """
    Decrypt base64url-encoded AES-256-GCM ciphertext.
    Raises VaultDecryptionError if corrupted or tampered.
    """
    key_bytes = _parse_key(key_input)
    try:
        parts = cipher_str.split(".")
        if len(parts) != 2:
            raise VaultDecryptionError("Invalid ciphertext format: expected {iv}.{ciphertext}")

        iv_padded = parts[0] + "=" * (-len(parts[0]) % 4)
        ct_padded = parts[1] + "=" * (-len(parts[1]) % 4)
        iv = base64.urlsafe_b64decode(iv_padded.encode("utf-8"))
        ciphertext = base64.urlsafe_b64decode(ct_padded.encode("utf-8"))

        aesgcm = AESGCM(key_bytes)
        plain_bytes = aesgcm.decrypt(iv, ciphertext, None)
        return plain_bytes.decode("utf-8")
    except VaultDecryptionError:
        raise
    except Exception as e:
        raise VaultDecryptionError(f"Decryption failed: {str(e)}") from e

async def resolve_member_key(api_key: str) -> Optional[dict[str, str]]:
    """
    Resolve and decrypt a member's credentials using Supabase Vault and Redis cache.
    Returns: {"nim": str, "elearning_pass": str, "studentv2_pass": str} or None.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY or not settings.VAULT_ENCRYPTION_KEY:
        return None

    stripped_key = api_key.strip()
    if not stripped_key:
        return None

    key_hash = hashlib.sha256(stripped_key.encode("utf-8")).hexdigest()
    cache_key = f"ubsi:vault:{key_hash}"

    # 1. Cek Redis Cache
    try:
        cached = await cache.get_fresh(cache_key)
        if cached and isinstance(cached, dict):
            return cached
    except Exception:
        pass

    # 2. Query Supabase REST API
    headers = {
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "Accept": "application/json"
    }
    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/api_keys"
    params = {
        "key_hash": f"eq.{key_hash}",
        "is_active": "eq.true",
        "select": "nim,encrypted_elearning_pass,encrypted_studentv2_pass"
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            if resp.status_code != 200:
                return None
            rows = resp.json()
            if not rows or not isinstance(rows, list):
                return None

            row = rows[0]
            el_pass = decrypt_credential(row["encrypted_elearning_pass"], settings.VAULT_ENCRYPTION_KEY)
            sv_pass = decrypt_credential(row["encrypted_studentv2_pass"], settings.VAULT_ENCRYPTION_KEY)

            data = {
                "nim": str(row["nim"]),
                "elearning_pass": el_pass,
                "studentv2_pass": sv_pass
            }

            try:
                # Cache selama 10 menit (600 detik)
                await cache.set(cache_key, data, ttl=600)
            except Exception:
                pass

            return data
    except Exception:
        return None

