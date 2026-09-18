"""BB84 quantum key distribution with an optional intercept-resend eavesdropper.

The qubits never interact and every gate is a Clifford gate, so the code packs
them into circuits of up to 64 qubits and runs those on Aer's stabilizer
method in a single job.

Bases are 0 for Z (|0>, |1>) and 1 for X (|+>, |->).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer import AerSimulator

Z, X = 0, 1

# Shor-Preskill: one-way post-processing can still distil a secret key up to ~11% QBER.
QBER_LIMIT = 0.11

CHUNK = 64


@dataclass(frozen=True)
class BB84Result:
    alice_bits: np.ndarray
    alice_bases: np.ndarray
    bob_bases: np.ndarray
    bob_bits: np.ndarray
    eve_bases: np.ndarray | None
    sifted: np.ndarray  # positions where Alice and Bob used the same basis
    checked: np.ndarray  # sifted positions revealed to estimate the error rate
    qber: float
    alice_key: str
    bob_key: str

    @property
    def aborted(self) -> bool:
        return self.qber > QBER_LIMIT


def bb84_circuit(
    alice_bits: np.ndarray,
    alice_bases: np.ndarray,
    bob_bases: np.ndarray,
    eve_bases: np.ndarray | None = None,
) -> QuantumCircuit:
    n = len(alice_bits)
    bob = ClassicalRegister(n, "bob")
    qc = QuantumCircuit(QuantumRegister(n, "q"), bob)

    def on(mask: np.ndarray) -> list[int]:
        return np.flatnonzero(mask).tolist()

    if ones := on(alice_bits == 1):
        qc.x(ones)
    if alice_x := on(alice_bases == X):
        qc.h(alice_x)

    if eve_bases is not None:
        eve = ClassicalRegister(n, "eve")
        qc.add_register(eve)
        qc.barrier()
        # Eve measures in her basis and sends on the state she measured.
        eve_x = on(eve_bases == X)
        if eve_x:
            qc.h(eve_x)
        qc.measure(range(n), eve)
        if eve_x:
            qc.h(eve_x)

    qc.barrier()
    if bob_x := on(bob_bases == X):
        qc.h(bob_x)
    qc.measure(range(n), bob)
    return qc


def _register_bits(qc: QuantumCircuit, memory: str) -> dict[str, np.ndarray]:
    # Memory lists registers last-first, each with bit 0 on the right.
    parts = memory.split()
    return {
        reg.name: np.array([int(b) for b in reversed(part)])
        for reg, part in zip(reversed(qc.cregs), parts, strict=True)
    }


def run(
    n_bits: int = 100,
    eavesdrop: bool = False,
    check_fraction: float = 0.5,
    seed: int | None = None,
) -> BB84Result:
    """Run the protocol once: send, sift, reveal a sample, estimate the QBER."""
    if n_bits < 1:
        raise ValueError("n_bits must be positive")
    if not 0 < check_fraction < 1:
        raise ValueError("check_fraction must be between 0 and 1")

    rng = np.random.default_rng(seed)
    alice_bits = rng.integers(2, size=n_bits)
    alice_bases = rng.integers(2, size=n_bits)
    bob_bases = rng.integers(2, size=n_bits)
    eve_bases = rng.integers(2, size=n_bits) if eavesdrop else None

    chunks = [slice(i, i + CHUNK) for i in range(0, n_bits, CHUNK)]
    circuits = [
        bb84_circuit(
            alice_bits[c], alice_bases[c], bob_bases[c], None if eve_bases is None else eve_bases[c]
        )
        for c in chunks
    ]
    backend = AerSimulator(method="stabilizer")
    result = backend.run(
        circuits, shots=1, memory=True, seed_simulator=int(rng.integers(2**31))
    ).result()
    bob_bits = np.concatenate(
        [_register_bits(qc, result.get_memory(qc)[0])["bob"] for qc in circuits]
    )

    sifted = np.flatnonzero(alice_bases == bob_bases)
    if len(sifted) == 0:
        checked = sifted
    else:
        k = max(1, round(len(sifted) * check_fraction))
        checked = np.sort(rng.choice(sifted, size=k, replace=False))
    kept = np.setdiff1d(sifted, checked)
    qber = float(np.mean(alice_bits[checked] != bob_bits[checked])) if len(checked) else 0.0

    return BB84Result(
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        bob_bits=bob_bits,
        eve_bases=eve_bases,
        sifted=sifted,
        checked=checked,
        qber=qber,
        alice_key="".join(map(str, alice_bits[kept])),
        bob_key="".join(map(str, bob_bits[kept])),
    )
