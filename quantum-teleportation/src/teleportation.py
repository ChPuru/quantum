"""Quantum teleportation of one qubit on the Qiskit Aer simulator.

Circuit layout follows the teleportation chapter of the Qiskit Textbook
(Apache-2.0, see NOTICE).

Qubits: q0 holds the message, q1 is Alice's half of the Bell pair, q2 is Bob's.
"""

from __future__ import annotations

from dataclasses import dataclass

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import (
    DensityMatrix,
    Pauli,
    Statevector,
    partial_trace,
    random_statevector,
    state_fidelity,
)
from qiskit_aer import AerSimulator


@dataclass(frozen=True)
class TeleportResult:
    message: Statevector
    received: DensityMatrix  # Bob's qubit after the corrections
    z_bit: int  # Alice's measurement of q0
    x_bit: int  # Alice's measurement of q1
    fidelity: float


def teleportation_circuit(message: Statevector | None = None) -> QuantumCircuit:
    """Build the protocol. If `message` is given, q0 is prepared in it first."""
    q = QuantumRegister(3, "q")
    z = ClassicalRegister(1, "z")
    x = ClassicalRegister(1, "x")
    qc = QuantumCircuit(q, z, x)

    if message is not None:
        qc.initialize(message, 0)
        qc.barrier()

    # Shared Bell pair between Alice (q1) and Bob (q2).
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()

    # Alice measures q0 and q1 in the Bell basis.
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, z)
    qc.measure(1, x)
    qc.barrier()

    # Bob fixes his qubit using the two classical bits.
    with qc.if_test((x, 1)):
        qc.x(2)
    with qc.if_test((z, 1)):
        qc.z(2)

    return qc


def teleport(message: Statevector, seed: int | None = None) -> TeleportResult:
    """Run one shot and compare Bob's qubit with the message.

    Alice's measurement outcome is random, so Bob's qubit is read off with a
    partial trace over q0 and q1 instead of picking fixed amplitudes. That
    works for all four outcomes.
    """
    qc = teleportation_circuit(message)
    qc.save_statevector()

    backend = AerSimulator()
    result = backend.run(transpile(qc, backend), shots=1, seed_simulator=seed).result()

    # Counts keys list registers last-first, so "x z".
    x_bit, z_bit = (int(b) for b in next(iter(result.get_counts())).split())
    received = partial_trace(result.get_statevector(), [0, 1])
    return TeleportResult(
        message=message,
        received=received,
        z_bit=z_bit,
        x_bit=x_bit,
        fidelity=state_fidelity(received, message),
    )


def random_message(seed: int | None = None) -> Statevector:
    return random_statevector(2, seed=seed)


def bloch_vector(state: Statevector | DensityMatrix) -> tuple[float, float, float]:
    """(<X>, <Y>, <Z>) for a single-qubit state."""
    x, y, z = (float(state.expectation_value(Pauli(p)).real) for p in "XYZ")
    return x, y, z
