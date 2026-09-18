"""Three-qubit bit-flip code with syndrome measurement and feed-forward correction.

Qubits: q0-q2 hold the code word, q3 and q4 are ancillas.
q3 measures the parity of q0 and q1, q4 the parity of q1 and q2, and the
two-bit syndrome s = q3 + 2*q4 points at the flipped qubit:

    s = 0  no error
    s = 1  q0 flipped
    s = 3  q1 flipped
    s = 2  q2 flipped

The code corrects any single bit flip. Two or more flips produce a logical X.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace, state_fidelity
from qiskit_aer import AerSimulator
from qiskit_aer.noise import pauli_error

SYNDROME_TO_QUBIT = {1: 0, 3: 1, 2: 2}


@dataclass(frozen=True)
class CorrectionResult:
    syndrome: int
    corrected_qubit: int | None
    decoded: DensityMatrix  # q0 after decoding
    fidelity: float  # against the input state


def encode(qc: QuantumCircuit) -> None:
    qc.cx(0, 1)
    qc.cx(0, 2)


def decode(qc: QuantumCircuit) -> None:
    qc.cx(0, 2)
    qc.cx(0, 1)


def measure_and_correct(qc: QuantumCircuit, syndrome: ClassicalRegister) -> None:
    qc.cx(0, 3)
    qc.cx(1, 3)
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.measure(3, syndrome[0])
    qc.measure(4, syndrome[1])
    for value, qubit in SYNDROME_TO_QUBIT.items():
        with qc.if_test((syndrome, value)):
            qc.x(qubit)


def bit_flip_circuit(
    state: Statevector | None = None, errors: Sequence[int] = ()
) -> QuantumCircuit:
    """Prepare, encode, flip the qubits in `errors`, correct, decode."""
    if any(q not in (0, 1, 2) for q in errors):
        raise ValueError("errors can only hit data qubits 0, 1 and 2")

    syndrome = ClassicalRegister(2, "syndrome")
    qc = QuantumCircuit(QuantumRegister(5, "q"), syndrome)
    if state is not None:
        qc.initialize(state, 0)
    encode(qc)
    qc.barrier()
    for q in errors:
        qc.x(q)
    qc.barrier()
    measure_and_correct(qc, syndrome)
    qc.barrier()
    decode(qc)
    return qc


def run(
    state: Statevector, errors: Sequence[int] = (), seed: int | None = None
) -> CorrectionResult:
    """Run one shot and compare the decoded q0 with the input state."""
    qc = bit_flip_circuit(state, errors)
    qc.save_statevector()
    backend = AerSimulator()
    result = backend.run(transpile(qc, backend), shots=1, seed_simulator=seed).result()

    syndrome = int(next(iter(result.get_counts())), 2)
    decoded = partial_trace(result.get_statevector(), [1, 2, 3, 4])
    return CorrectionResult(
        syndrome=syndrome,
        corrected_qubit=SYNDROME_TO_QUBIT.get(syndrome),
        decoded=decoded,
        fidelity=state_fidelity(decoded, state),
    )


def logical_error_rate(p: float, shots: int = 4000, seed: int | None = None) -> float:
    """Encode |0>, flip each data qubit with probability p, correct, and count logical flips.

    Theory says 3p^2 - 2p^3, against p for a bare qubit.
    """
    syndrome = ClassicalRegister(2, "syndrome")
    out = ClassicalRegister(1, "out")
    qc = QuantumCircuit(QuantumRegister(5, "q"), syndrome, out)
    encode(qc)
    noise = pauli_error([("X", p), ("I", 1 - p)])
    for q in range(3):
        qc.append(noise, [q])
    measure_and_correct(qc, syndrome)
    decode(qc)
    qc.measure(0, out[0])

    backend = AerSimulator()
    counts = (
        backend.run(transpile(qc, backend), shots=shots, seed_simulator=seed).result().get_counts()
    )
    # Keys look like "o ss": the out register comes first.
    flips = sum(c for key, c in counts.items() if key.split()[0] == "1")
    return flips / shots
