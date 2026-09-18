import pytest
from qiskit.quantum_info import Statevector, random_statevector

from src.bit_flip_code import bit_flip_circuit, logical_error_rate, run

STATES = [Statevector.from_label(s) for s in "01+-r"] + [random_statevector(2, seed=9)]


@pytest.mark.parametrize("state", STATES)
@pytest.mark.parametrize(("errors", "syndrome"), [((), 0), ((0,), 1), ((1,), 3), ((2,), 2)])
def test_single_errors_are_corrected(
    state: Statevector, errors: tuple[int, ...], syndrome: int
) -> None:
    result = run(state, errors, seed=0)
    assert result.syndrome == syndrome
    assert result.fidelity == pytest.approx(1.0)


def test_corrected_qubit_matches_error() -> None:
    for q in range(3):
        assert run(Statevector.from_label("0"), [q]).corrected_qubit == q
    assert run(Statevector.from_label("0")).corrected_qubit is None


@pytest.mark.parametrize("errors", [(0, 1), (1, 2), (0, 2), (0, 1, 2)])
def test_two_or_more_errors_cause_a_logical_flip(errors: tuple[int, ...]) -> None:
    # |0> comes back as |1>.
    assert run(Statevector.from_label("0"), errors).fidelity == pytest.approx(0.0)


def test_rejects_errors_on_ancillas() -> None:
    with pytest.raises(ValueError):
        bit_flip_circuit(errors=[3])


def test_circuit_uses_feed_forward() -> None:
    ops = bit_flip_circuit().count_ops()
    assert ops["if_else"] == 3
    assert ops["measure"] == 2


@pytest.mark.parametrize("p", [0.05, 0.1, 0.2])
def test_logical_error_rate_follows_theory(p: float) -> None:
    rate = logical_error_rate(p, shots=20000, seed=4)
    assert rate == pytest.approx(3 * p**2 - 2 * p**3, abs=0.01)
    assert rate < p
