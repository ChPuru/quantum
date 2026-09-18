import itertools

import numpy as np
import pytest
from qiskit.quantum_info import Operator, Statevector

from src.grover import (
    diffuser,
    expected_success,
    optimal_iterations,
    phase_oracle,
    search,
)


def all_strings(n: int) -> list[str]:
    return ["".join(bits) for bits in itertools.product("01", repeat=n)]


@pytest.mark.parametrize("marked", [["101"], ["110", "001"], ["0110"]])
def test_oracle_flips_only_marked_states(marked: list[str]) -> None:
    n = len(marked[0])
    op = Operator(phase_oracle(marked))
    for s in all_strings(n):
        state = Statevector.from_label(s)
        sign = -1 if s in marked else 1
        assert np.isclose(state.inner(state.evolve(op)), sign)


@pytest.mark.parametrize("n", [2, 3, 4])
def test_diffuser_reflects_about_uniform_state(n: int) -> None:
    s = Statevector.from_label("+" * n).data
    reflection = 2 * np.outer(s, s.conj()) - np.eye(2**n)
    assert Operator(diffuser(n)).equiv(Operator(reflection))


def test_iteration_counts() -> None:
    assert optimal_iterations(2, 1) == 1
    assert optimal_iterations(3, 1) == 2
    assert optimal_iterations(4, 1) == 3
    assert optimal_iterations(6, 1) == 6
    assert expected_success(2, 1, 1) == pytest.approx(1.0)


def test_bit_order_matches_counts() -> None:
    # "110" means qubit 2 = 1, qubit 1 = 1, qubit 0 = 0, same as Qiskit's counts keys.
    assert search(["110"], seed=1).most_frequent == "110"


@pytest.mark.parametrize("target", ["01", "101", "0110", "11010"])
def test_finds_single_marked_string(target: str) -> None:
    result = search([target], shots=2048, seed=7)
    assert result.most_frequent == target
    assert result.success_rate == pytest.approx(result.expected_success, abs=0.05)


def test_finds_several_marked_strings() -> None:
    marked = ["0011", "1100", "1010"]
    result = search(marked, shots=4096, seed=3)
    top3 = sorted(result.counts, key=result.counts.__getitem__, reverse=True)[:3]
    assert set(top3) == set(marked)
    assert result.success_rate == pytest.approx(result.expected_success, abs=0.05)


def test_zero_iterations_is_uniform_guess() -> None:
    result = search(["111"], iterations=0, shots=8000, seed=0)
    assert result.success_rate == pytest.approx(1 / 8, abs=0.02)


@pytest.mark.parametrize("marked", [[], ["1"], ["10", "101"], ["10a"], ["00", "01", "10", "11"]])
def test_rejects_bad_input(marked: list[str]) -> None:
    with pytest.raises(ValueError):
        search(marked)
