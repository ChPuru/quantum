# tests/test_secure_storage.py

import unittest
import os
from src.bb84_key_exchange import BB84KeyExchange
from src.classical_crypto import ClassicalCrypto

class TestSecureStorage(unittest.TestCase):

    def test_end_to_end_cycle(self):
        """
        Tests the full cycle: key generation, encryption, and decryption.
        """
        # 1. Generate a key
        qkd = BB84KeyExchange()
        key = qkd.generate_secure_key(key_length_bytes=32)
        self.assertEqual(len(key), 32)

        # 2. Encrypt some data
        crypto_system = ClassicalCrypto(key=key)
        original_data = b"test data for the cycle"
        nonce, ciphertext = crypto_system.encrypt(original_data)

        # 3. Decrypt the data
        decrypted_data = crypto_system.decrypt(nonce, ciphertext)
        
        # 4. Verify
        self.assertEqual(original_data, decrypted_data)

    def test_decryption_failure_with_wrong_key(self):
        """
        Tests that decryption fails if the wrong key is used.
        """
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        self.assertNotEqual(key1, key2)

        crypto1 = ClassicalCrypto(key=key1)
        original_data = b"some secret message"
        nonce, ciphertext = crypto1.encrypt(original_data)

        # Try to decrypt with the wrong key
        crypto2 = ClassicalCrypto(key=key2)
        decrypted_data = crypto2.decrypt(nonce, ciphertext)

        self.assertIsNone(decrypted_data)

if __name__ == '__main__':
    unittest.main()