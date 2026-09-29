import pytest
from app.vault import (
    encrypt_credential,
    decrypt_credential,
    VaultDecryptionError,
)

def test_aes_gcm_roundtrip():
    # 64-hex char key (32 bytes)
    key_hex = "0123456789abcdef" * 4
    plain = "PasswordKampus123!#@$"
    
    encrypted = encrypt_credential(plain, key_hex)
    assert encrypted != plain
    assert "." in encrypted
    
    decrypted = decrypt_credential(encrypted, key_hex)
    assert decrypted == plain

def test_aes_gcm_roundtrip_raw_32bytes_str():
    # Raw 32 bytes string
    key_raw = "12345678901234567890123456789012"
    plain = "RahasiaSIAKAD2026"
    
    encrypted = encrypt_credential(plain, key_raw)
    decrypted = decrypt_credential(encrypted, key_raw)
    assert decrypted == plain

def test_aes_gcm_tampered_fails():
    key_hex = "0123456789abcdef" * 4
    encrypted = encrypt_credential("Secret123", key_hex)
    parts = encrypted.split(".")
    
    # Tamper with the ciphertext portion
    tampered_ct = parts[1][:-2] + ("aa" if not parts[1].endswith("aa") else "bb")
    tampered = f"{parts[0]}.{tampered_ct}"
    
    with pytest.raises(VaultDecryptionError):
        decrypt_credential(tampered, key_hex)

def test_invalid_key_length():
    with pytest.raises(ValueError):
        encrypt_credential("Secret", "short_key")

def test_invalid_cipher_format():
    key_hex = "0123456789abcdef" * 4
    with pytest.raises(VaultDecryptionError):
        decrypt_credential("not_a_valid_dot_delimited_cipher", key_hex)
