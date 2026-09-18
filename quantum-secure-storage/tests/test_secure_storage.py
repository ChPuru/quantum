import os

import pytest
from cryptography.exceptions import InvalidTag

from src.bb84_key_exchange import KEY_BYTES, EavesdropperDetected, exchange_key
from src.classical_crypto import NONCE_BYTES, decrypt, encrypt


def test_honest_exchange_gives_matching_keys() -> None:
    kx = exchange_key(seed=1)
    assert kx.alice_key == kx.bob_key
    assert len(kx.alice_key) == KEY_BYTES
    assert kx.qber == 0.0


def test_different_seeds_give_different_keys() -> None:
    assert exchange_key(seed=1).alice_key != exchange_key(seed=2).alice_key


def test_eavesdropper_is_detected() -> None:
    with pytest.raises(EavesdropperDetected):
        exchange_key(eavesdrop=True, seed=3)


def test_round_trip() -> None:
    key = exchange_key(seed=4).alice_key
    blob = encrypt(key, b"secret")
    assert len(blob) == NONCE_BYTES + len(b"secret") + 16  # 16-byte GCM tag
    assert decrypt(key, blob) == b"secret"


def test_nonce_changes_every_time() -> None:
    key = os.urandom(32)
    assert encrypt(key, b"same") != encrypt(key, b"same")


def test_wrong_key_is_rejected() -> None:
    blob = encrypt(os.urandom(32), b"secret")
    with pytest.raises(InvalidTag):
        decrypt(os.urandom(32), blob)


def test_tampering_is_rejected() -> None:
    key = os.urandom(32)
    blob = bytearray(encrypt(key, b"secret"))
    blob[-1] ^= 1
    with pytest.raises(InvalidTag):
        decrypt(key, bytes(blob))


def test_associated_data_must_match() -> None:
    key = os.urandom(32)
    blob = encrypt(key, b"secret", associated_data=b"file-1")
    assert decrypt(key, blob, associated_data=b"file-1") == b"secret"
    with pytest.raises(InvalidTag):
        decrypt(key, blob, associated_data=b"file-2")
