"""Grover search over n-qubit bitstrings on the Qiskit Aer simulator.

The diffuser follows the Grover's algorithm chapter of the Qiskit Textbook
(Apache-2.0, see NOTICE).

Bitstrings use Qiskit's ordering: the leftmost character is the highest qubit,
so the string you mark is the string that shows up in the counts.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


@dataclass(frozen=True)
class SearchResult:
    counts: dict[str, int]
    iterations: int
    success_rate: float  # fraction of shots that hit a marked string
    expected_success: float  # sin^2((2k + 1) * theta)

    @property
    def most_frequent(self) -> str:
        return max(self.counts, key=self.counts.__getitem__)


def _check_marked(marked: Sequence[str]) -> int:
    if not marked:
        raise ValueError("mark at least one bitstring")
    n = len(marked[0])
    if n < 2:
        raise ValueError("use at least 2 qubits")
    for s in marked:
        if len(s) != n or set(s) - {"0", "1"}:
            raise ValueError(f"{s!r} is not a {n}-bit binary string")
    if len(set(marked)) == 2**n:
        raise ValueError("every bitstring is marked; there is nothing to search for")
    return n


def _mcz(qc: QuantumCircuit) -> None:
    """Phase-flip |11...1> with an H-MCX-H sandwich on the top qubit."""
    top = qc.num_qubits - 1
    qc.h(top)
    qc.mcx(list(range(top)), top)
    qc.h(top)


def phase_oracle(marked: Sequence[str]) -> QuantumCircuit:
    """Flip the sign of every marked basis state."""
    n = _check_marked(marked)
    qc = QuantumCircuit(n, name="oracle")
    for target in dict.fromkeys(marked):
        # Character k of the string belongs to qubit n - 1 - k.
        zeros = [q for q in range(n) if target[n - 1 - q] == "0"]
        if zeros:
            qc.x(zeros)
        _mcz(qc)
        if zeros:
            qc.x(zeros)
    return qc


def diffuser(n: int) -> QuantumCircuit:
    """Reflection about the uniform superposition, up to a global phase of -1."""
    qc = QuantumCircuit(n, name="diffuser")
    qc.h(range(n))
    qc.x(range(n))
    _mcz(qc)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def optimal_iterations(n: int, num_marked: int) -> int:
    """floor(pi / (4 * theta)) with sin(theta) = sqrt(M / N)."""
    theta = math.asin(math.sqrt(num_marked / 2**n))
    return math.floor(math.pi / (4 * theta))


def expected_success(n: int, num_marked: int, iterations: int) -> float:
    theta = math.asin(math.sqrt(num_marked / 2**n))
    return math.sin((2 * iterations + 1) * theta) ** 2


def grover_circuit(marked: Sequence[str], iterations: int | None = None) -> QuantumCircuit:
    n = _check_marked(marked)
    num_marked = len(set(marked))
    k = optimal_iterations(n, num_marked) if iterations is None else iterations

    oracle = phase_oracle(marked).to_gate()
    diff = diffuser(n).to_gate()

    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(k):
        qc.append(oracle, range(n))
        qc.append(diff, range(n))
    qc.measure_all()
    return qc


def search(
    marked: Sequence[str],
    shots: int = 1024,
    iterations: int | None = None,
    seed: int | None = None,
) -> SearchResult:
    n = _check_marked(marked)
    num_marked = len(set(marked))
    k = optimal_iterations(n, num_marked) if iterations is None else iterations

    backend = AerSimulator()
    circuit = transpile(grover_circuit(marked, k), backend)
    counts = backend.run(circuit, shots=shots, seed_simulator=seed).result().get_counts()

    hits = sum(counts.get(s, 0) for s in set(marked))
    return SearchResult(
        counts=dict(counts),
        iterations=k,
        success_rate=hits / shots,
        expected_success=expected_success(n, num_marked, k),
    )
