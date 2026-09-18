"""AES-256-GCM encryption for the stored data.

GCM authenticates as well as encrypts: decrypting with the wrong key, or
decrypting a ciphertext someone edited, raises cryptography's InvalidTag.
The 12-byte random nonce goes in front of the ciphertext.
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_BYTES = 12


def encrypt(key: bytes, plaintext: bytes, associated_data: bytes | None = None) -> bytes:
    nonce = os.urandom(NONCE_BYTES)
    return nonce + AESGCM(key).encrypt(nonce, plaintext, associated_data)


def decrypt(key: bytes, blob: bytes, associated_data: bytes | None = None) -> bytes:
    nonce, ciphertext = blob[:NONCE_BYTES], blob[NONCE_BYTES:]
    return AESGCM(key).decrypt(nonce, ciphertext, associated_data)
