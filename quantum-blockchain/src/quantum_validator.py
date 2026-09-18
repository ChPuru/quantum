"""Turn a block hash into a small circuit and check which bitstring it favours.

This is a toy proof of work. SHA-256 already makes the outcome unpredictable,
and a 4-qubit circuit is trivial to simulate classically, which is exactly
what this code does. Running the circuit on quantum hardware would add noise,
not security. The point is practice at building circuits from data.
"""

from __future__ import annotations

import math

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


class QuantumValidator:
    """A block is valid when `target` is the single most likely outcome of its circuit."""

    def __init__(self, num_qubits: int = 4, target: str | None = None) -> None:
        target = "1" * num_qubits if target is None else target
        if num_qubits < 1 or len(target) != num_qubits or set(target) - {"0", "1"}:
            raise ValueError(f"target must be a {num_qubits}-bit binary string")
        self.num_qubits = num_qubits
        self.target = target

    def circuit(self, block_hash: str) -> QuantumCircuit:
        """One gate per hex digit, cycling over the qubits.

        0-3 -> H, 4-7 -> X, 8-b -> CX from the next qubit, c-f -> RZ(digit * pi / 8).
        """
        n = self.num_qubits
        qc = QuantumCircuit(n)
        for i, digit in enumerate(block_hash):
            value = int(digit, 16)
            q = i % n
            if value < 4:
                qc.h(q)
            elif value < 8:
                qc.x(q)
            elif value < 12:
                if n > 1:
                    qc.cx((q + 1) % n, q)
            else:
                qc.rz(value * math.pi / 8, q)
        return qc

    def probabilities(self, block_hash: str) -> dict[str, float]:
        """Exact outcome probabilities. No sampling, so validation is repeatable."""
        return Statevector(self.circuit(block_hash)).probabilities_dict()

    def is_valid(self, block_hash: str) -> bool:
        probs = self.probabilities(block_hash)
        p_target = probs.get(self.target, 0.0)
        others = (p for key, p in probs.items() if key != self.target)
        return p_target > max(others, default=0.0) + 1e-9
