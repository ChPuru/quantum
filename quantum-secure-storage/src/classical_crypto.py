# src/classical_crypto.py

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class ClassicalCrypto:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes long for AES-256.")
        self.key = key
        self.backend = default_backend()

    def encrypt(self, plaintext: bytes) -> (bytes, bytes, bytes):
        """
        Encrypts plaintext using AES-256 in GCM mode.

        Returns:
            (bytes, bytes, bytes): A tuple containing the (nonce, ciphertext, tag).
        """
        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce), backend=self.backend)
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        # THE FIX: We must also return the authentication tag.
        return nonce, ciphertext, encryptor.tag

    def decrypt(self, nonce: bytes, ciphertext: bytes, tag: bytes) -> bytes:
        """
        Decrypts ciphertext using AES-256 in GCM mode.
        """
        # THE FIX: The tag must be provided to the GCM mode.
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce, tag), backend=self.backend)
        decryptor = cipher.decryptor()
        
        try:
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
        except Exception:
            # GCM will raise an error if the key is wrong or the data is tampered with.
            return None