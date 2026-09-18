# BB84 key exchange feeding AES-GCM storage

Alice and Bob agree on a 256-bit key with simulated BB84, then Alice encrypts data with AES-256-GCM and Bob decrypts it. A wrong key or an edited ciphertext gets rejected, and an intercept-resend eavesdropper makes the key exchange abort.

## Run

```bash
pip install -r requirements.txt
python -m src.main
python -m pytest
```

```
$ python -m src.main
qubits sent         2048
QBER                0.0%
keys match          True
stored blob         dfd67ef620e01f928233d4649e63a400d69ea64e5646e1ae...
Bob decrypts        b'meet at the usual place, 7pm'
wrong key           rejected (InvalidTag)
edited blob         rejected (InvalidTag)
with Eve            aborted: QBER 21.4% is above 11%
```

## How it works

- `bb84_key_exchange.py` runs BB84 rounds of 1024 qubits until 512 unrevealed matching-basis bits exist, checking the error rate on a 25% sample as it goes and aborting above 11%. SHA-256 compresses the 512 bits into the 32-byte key. Real systems use error correction and universal hashing here instead.
- `classical_crypto.py` wraps AES-256-GCM from the `cryptography` package. The random 12-byte nonce is stored in front of the ciphertext, and GCM's tag makes decryption fail loudly on a wrong key or edited data.

## Limits

The keys this produces are **not secret**. The randomness comes from NumPy's seeded generator and the "quantum channel" is a simulator. The project shows how a QKD key would plug into ordinary encryption, nothing more.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.
