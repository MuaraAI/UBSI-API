import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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
