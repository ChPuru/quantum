"""Shor's factoring algorithm on the Qiskit Aer simulator.

The quantum step is order finding: for a coprime to N, find the smallest r > 0
with a**r = 1 (mod N). The rest is classical number theory.

The phase-estimation layout follows the Shor's algorithm chapter of the Qiskit
Textbook (Apache-2.0, see NOTICE). Modular multiplication is built as a
permutation matrix, which is exact but grows exponentially with the bit length
of N. That limits this code to small N on a simulator. Real hardware needs
reversible arithmetic circuits instead.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from fractions import Fraction

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFTGate, UnitaryGate
from qiskit_aer import AerSimulator

# 7-bit N needs 21 qubits and ~15 s per attempt. 8 bits would need 24 qubits.
MAX_BITS = 7


@dataclass(frozen=True)
class FactorResult:
    n: int
    factors: tuple[int, int]
    method: str  # "even", "perfect power", "gcd" or "order finding"
    a: int | None = None
    order: int | None = None
    attempts: int = 0


def controlled_mult_mod(a: int, n: int, num_bits: int) -> UnitaryGate:
    """Controlled |x> -> |a*x mod n> on `num_bits` target qubits.

    Qubit 0 of the gate is the control. Basis states with x >= n are left
    alone, which keeps the matrix a permutation. Requires gcd(a, n) == 1.
    """
    if math.gcd(a, n) != 1:
        raise ValueError(f"a={a} is not coprime to n={n}")
    dim = 2**num_bits
    matrix = np.zeros((2 * dim, 2 * dim))
    # Qiskit is little-endian: with the control on qubit 0, index = ctrl + 2*x.
    for x in range(dim):
        y = (a * x) % n if x < n else x
        matrix[2 * x, 2 * x] = 1
        matrix[2 * y + 1, 2 * x + 1] = 1
    return UnitaryGate(matrix, label=f"{a}x mod {n}")


def order_finding_circuit(a: int, n: int) -> QuantumCircuit:
    """Phase estimation of x -> a*x mod n, with 2*bits(n) counting qubits."""
    num_bits = n.bit_length()
    num_counting = 2 * num_bits
    work = list(range(num_counting, num_counting + num_bits))

    qc = QuantumCircuit(num_counting + num_bits, num_counting)
    qc.h(range(num_counting))
    qc.x(work[0])  # work register starts in |1>

    # Counting qubit j controls U^(2^j). Computing a^(2^j) mod n classically
    # gives that power as a single multiplication.
    for j in range(num_counting):
        qc.append(controlled_mult_mod(pow(a, 2**j, n), n, num_bits), [j, *work])

    qc.append(QFTGate(num_counting).inverse(), range(num_counting))
    qc.measure(range(num_counting), range(num_counting))
    return qc


def order_from_counts(counts: dict[str, int], a: int, n: int) -> int | None:
    """Recover r from phase-estimation counts with continued fractions.

    A reading y gives y / 2^t ~ s/r. When gcd(s, r) > 1 the denominator is only
    a divisor of r, so this also tries the lcm of the denominators seen so far.
    Returns r with a**r = 1 (mod n), or None if no reading worked.
    """
    r = 1
    for bits, _ in sorted(counts.items(), key=lambda item: -item[1]):
        phase = Fraction(int(bits, 2), 2 ** len(bits))
        d = phase.limit_denominator(n).denominator
        if pow(a, d, n) == 1:
            return d
        r = math.lcm(r, d)
        if pow(a, r, n) == 1:
            return r
    return None


def find_order(a: int, n: int, shots: int = 16, seed: int | None = None) -> int | None:
    """Run order finding for a mod n on the simulator."""
    backend = AerSimulator()
    circuit = transpile(order_finding_circuit(a, n), backend)
    counts = backend.run(circuit, shots=shots, seed_simulator=seed).result().get_counts()
    return order_from_counts(counts, a, n)


def factor(
    n: int,
    a: int | None = None,
    max_attempts: int = 10,
    shots: int = 16,
    seed: int | None = None,
) -> FactorResult:
    """Find a non-trivial factor pair of n.

    Pass `a` to skip the random choice and force a particular base, e.g.
    factor(15, a=7). Raises ValueError for n that is prime, too small or too
    large to simulate, and RuntimeError if every attempt fails.
    """
    _check_input(n)

    if n % 2 == 0:
        return FactorResult(n, (2, n // 2), "even")
    base = _perfect_power_base(n)
    if base is not None:
        return FactorResult(n, (base, n // base), "perfect power")

    rng = random.Random(seed)
    for attempt in range(1, max_attempts + 1):
        base_a = a if a is not None else rng.randrange(2, n - 1)
        g = math.gcd(base_a, n)
        if g > 1:
            # A lucky guess. Real Shor runs hit this with tiny N all the time.
            return FactorResult(n, (g, n // g), "gcd", a=base_a, attempts=attempt)

        r = find_order(base_a, n, shots=shots, seed=rng.randrange(2**31))
        if r is None or r % 2 == 1:
            continue
        x = pow(base_a, r // 2, n)
        if x == n - 1:
            continue
        for p in (math.gcd(x - 1, n), math.gcd(x + 1, n)):
            if 1 < p < n:
                return FactorResult(
                    n, (p, n // p), "order finding", a=base_a, order=r, attempts=attempt
                )

    raise RuntimeError(f"no factor of {n} found in {max_attempts} attempts")


def _check_input(n: int) -> None:
    if n < 4:
        raise ValueError("n must be a composite number >= 4")
    if n.bit_length() > MAX_BITS:
        raise ValueError(f"n={n} needs more than {MAX_BITS} bits; too large to simulate")
    if _is_prime(n):
        raise ValueError(f"{n} is prime")


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % d for d in range(2, math.isqrt(n) + 1))


def _perfect_power_base(n: int) -> int | None:
    """Return b if n == b**k for some k >= 2, else None."""
    for k in range(2, n.bit_length() + 1):
        b = round(n ** (1 / k))
        for candidate in (b - 1, b, b + 1):
            if candidate > 1 and candidate**k == n:
                return candidate
    return None
