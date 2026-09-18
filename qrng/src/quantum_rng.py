"""Random bits from measuring a qubit in the |+> state.

Measuring |+> in the Z basis gives 0 or 1 with probability 1/2 each. On real
hardware that randomness comes from the measurement itself (plus some device
bias). On the Aer simulator it comes from Aer's pseudorandom number
generator, so the output here is pseudorandom and reproducible with a seed.
Treat this as a demo of the circuit, not as a source of secrets.
"""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def coin_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def random_bits(n: int, seed: int | None = None) -> str:
    """n bits, one per shot of the one-qubit circuit."""
    if n < 1:
        raise ValueError("n must be positive")
    job = AerSimulator().run(coin_circuit(), shots=n, memory=True, seed_simulator=seed)
    return "".join(job.result().get_memory())


def random_int(low: int, high: int, seed: int | None = None) -> int:
    """Uniform integer in [low, high].

    Draws just enough bits to cover the range and rejects values past the top,
    so every result is equally likely. Taking the bits mod the range size would
    favour small values.
    """
    if high < low:
        raise ValueError("high must be >= low")
    span = high - low + 1
    width = max(1, (span - 1).bit_length())
    # Each draw succeeds with probability > 1/2, so 64 draws almost never all fail.
    bits = random_bits(width * 64, seed=seed)
    for i in range(0, len(bits), width):
        value = int(bits[i : i + width], 2)
        if value < span:
            return low + value
    raise RuntimeError("rejection sampling failed 64 times in a row")
