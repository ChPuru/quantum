"""Agree on a 256-bit AES key with simulated BB84.

Each round sends qubits in random bases, keeps the positions where Alice and
Bob chose the same basis, and reveals part of those to estimate the error
rate. Above 11% the exchange aborts. The surviving bits are hashed down with
SHA-256, a stand-in for privacy amplification (real systems use universal
hashing with a length set by the measured error rate).

Everything here runs on a simulator with a seeded pseudorandom generator, so
the resulting keys are not secret. The project shows how the pieces fit.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer import AerSimulator

KEY_BYTES = 32
QBER_LIMIT = 0.11
CHUNK = 64  # qubits per circuit; they never interact, so small circuits are fine


class EavesdropperDetected(RuntimeError):
    pass


@dataclass(frozen=True)
class KeyExchange:
    alice_key: bytes
    bob_key: bytes
    qubits_sent: int
    raw_key_bits: int  # bits hashed into the final key
    qber: float


def _round(
    n: int, rng: np.random.Generator, eavesdrop: bool
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Send n qubits. Returns Alice's bits and bases, Bob's bases and results."""
    bits = rng.integers(2, size=n)
    a_bases = rng.integers(2, size=n)
    b_bases = rng.integers(2, size=n)
    e_bases = rng.integers(2, size=n)

    circuits = []
    for start in range(0, n, CHUNK):
        idx = range(start, min(start + CHUNK, n))
        creg = ClassicalRegister(len(idx), "bob")
        qc = QuantumCircuit(QuantumRegister(len(idx)), creg)
        for q, i in enumerate(idx):
            if bits[i]:
                qc.x(q)
            if a_bases[i]:
                qc.h(q)
            if eavesdrop:  # intercept-resend: measure in Eve's basis, send that state on
                if e_bases[i]:
                    qc.h(q)
                qc.measure(q, creg[q])
                if e_bases[i]:
                    qc.h(q)
            if b_bases[i]:
                qc.h(q)
        qc.measure(range(len(idx)), creg)
        circuits.append(qc)

    backend = AerSimulator(method="stabilizer")
    result = backend.run(
        circuits, shots=1, memory=True, seed_simulator=int(rng.integers(2**31))
    ).result()
    bob = np.concatenate([[int(b) for b in reversed(result.get_memory(qc)[0])] for qc in circuits])
    return bits, a_bases, b_bases, bob


def _to_key(bits: list[int]) -> bytes:
    return hashlib.sha256(np.packbits(np.array(bits, dtype=np.uint8)).tobytes()).digest()


def exchange_key(
    eavesdrop: bool = False,
    check_fraction: float = 0.25,
    round_size: int = 1024,
    seed: int | None = None,
) -> KeyExchange:
    """Run BB84 rounds until 512 unrevealed matching-basis bits exist, then hash to 32 bytes."""
    rng = np.random.default_rng(seed)
    target = 2 * KEY_BYTES * 8
    alice_kept: list[int] = []
    bob_kept: list[int] = []
    errors = checked = sent = 0

    while len(alice_kept) < target:
        bits, a_bases, b_bases, bob = _round(round_size, rng, eavesdrop)
        sent += round_size
        sifted = np.flatnonzero(a_bases == b_bases)
        reveal = rng.random(len(sifted)) < check_fraction
        errors += int(np.sum(bits[sifted[reveal]] != bob[sifted[reveal]]))
        checked += int(reveal.sum())
        alice_kept += bits[sifted[~reveal]].tolist()
        bob_kept += bob[sifted[~reveal]].tolist()

        qber = errors / checked if checked else 0.0
        if qber > QBER_LIMIT:
            raise EavesdropperDetected(f"QBER {qber:.1%} is above {QBER_LIMIT:.0%}")

    return KeyExchange(
        alice_key=_to_key(alice_kept[:target]),
        bob_key=_to_key(bob_kept[:target]),
        qubits_sent=sent,
        raw_key_bits=target,
        qber=errors / checked if checked else 0.0,
    )
