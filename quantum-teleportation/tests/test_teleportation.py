import pytest
from qiskit.quantum_info import Statevector

from src.teleportation import bloch_vector, random_message, teleport, teleportation_circuit


@pytest.mark.parametrize("label", ["0", "1", "+", "-", "r", "l"])
def test_teleports_basis_states(label: str) -> None:
    message = Statevector.from_label(label)
    for seed in range(8):
        assert teleport(message, seed=seed).fidelity == pytest.approx(1.0)


def test_every_measurement_outcome_works() -> None:
    message = random_message(seed=7)
    outcomes = set()
    for seed in range(40):
        result = teleport(message, seed=seed)
        assert result.fidelity == pytest.approx(1.0)
        outcomes.add((result.z_bit, result.x_bit))
    assert outcomes == {(0, 0), (0, 1), (1, 0), (1, 1)}


def test_random_messages() -> None:
    for seed in range(10):
        message = random_message(seed)
        assert teleport(message, seed=seed).fidelity == pytest.approx(1.0)


def test_bloch_vectors_match() -> None:
    message = random_message(seed=3)
    received = teleport(message, seed=3).received
    assert bloch_vector(received) == pytest.approx(bloch_vector(message))


def test_circuit_shape() -> None:
    qc = teleportation_circuit()
    assert qc.num_qubits == 3
    assert qc.num_clbits == 2
    assert qc.count_ops()["measure"] == 2
