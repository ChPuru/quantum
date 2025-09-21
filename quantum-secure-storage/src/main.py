# src/main.py

from src.bb84_key_exchange import BB84KeyExchange
from src.classical_crypto import ClassicalCrypto
import os

def main():
    print("--- Quantum Secure Cloud Storage Simulation ---")

    alice_secret_data = b"This is my top secret plan for the quantum project!"
    print(f"\nAlice's original data: {alice_secret_data}")

    qkd = BB84KeyExchange()
    secure_shared_key = qkd.generate_secure_key(key_length_bytes=32)

    alice_crypto = ClassicalCrypto(key=secure_shared_key)
    # THE FIX: Unpack all three return values.
    nonce, encrypted_data, tag = alice_crypto.encrypt(alice_secret_data)
    print(f"\nData encrypted with quantum-secured key.")
    print(f"  - Encrypted data (ciphertext): {encrypted_data.hex()}")

    print("\nBob retrieves the encrypted data and decrypts it...")
    bob_crypto = ClassicalCrypto(key=secure_shared_key)
    # THE FIX: Pass the tag to the decrypt method.
    decrypted_data = bob_crypto.decrypt(nonce, encrypted_data, tag)

    if decrypted_data:
        print(f"  -> Decryption successful!")
        print(f"  -> Bob's decrypted data: {decrypted_data}")
        assert alice_secret_data == decrypted_data
    else:
        print("  -> Decryption failed.")

    print("\nEve, an eavesdropper, tries to decrypt with a guessed key...")
    eve_guessed_key = os.urandom(32)
    eve_crypto = ClassicalCrypto(key=eve_guessed_key)
    # THE FIX: Pass the tag to Eve's decrypt method as well.
    eve_decrypted_data = eve_crypto.decrypt(nonce, encrypted_data, tag)

    if not eve_decrypted_data:
        print("  -> As expected, Eve's decryption attempt failed.")
    
    print("\n---------------------------------------------")

if __name__ == "__main__":
    main()