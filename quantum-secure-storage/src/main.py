import os

from cryptography.exceptions import InvalidTag

from src.bb84_key_exchange import EavesdropperDetected, exchange_key
from src.classical_crypto import decrypt, encrypt


def main() -> None:
    kx = exchange_key(seed=7)
    print(f"qubits sent         {kx.qubits_sent}")
    print(f"QBER                {kx.qber:.1%}")
    print(f"keys match          {kx.alice_key == kx.bob_key}")

    stored = encrypt(kx.alice_key, b"meet at the usual place, 7pm")
    print(f"stored blob         {stored.hex()[:48]}...")
    print(f"Bob decrypts        {decrypt(kx.bob_key, stored)!r}")

    for label, key, blob in [
        ("wrong key", os.urandom(32), stored),
        ("edited blob", kx.bob_key, stored[:-1] + bytes([stored[-1] ^ 1])),
    ]:
        try:
            decrypt(key, blob)
            print(f"{label:<20}decrypted?!")
        except InvalidTag:
            print(f"{label:<20}rejected (InvalidTag)")

    try:
        exchange_key(eavesdrop=True, seed=7)
    except EavesdropperDetected as err:
        print(f"with Eve            aborted: {err}")


if __name__ == "__main__":
    main()
