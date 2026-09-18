import math

import pytest
from qiskit.quantum_info import Operator, Statevector

from src.shors import (
    controlled_mult_mod,
    factor,
    find_order,
    order_finding_circuit,
    order_from_counts,
)


def classical_order(a: int, n: int) -> int:
    return next(r for r in range(1, n) if pow(a, r, n) == 1)


@pytest.mark.parametrize("a", [2, 4, 7, 8, 11, 13, 14])
def test_controlled_mult_mod_acts_on_basis_states(a: int) -> None:
    op = Operator(controlled_mult_mod(a, 15, 4))
    for x in range(15):
        for ctrl in (0, 1):
            out = Statevector.from_int(ctrl + 2 * x, 32).evolve(op)
            expected = (a * x) % 15 if ctrl else x
            assert out.equiv(Statevector.from_int(ctrl + 2 * expected, 32))


def test_controlled_mult_mod_rejects_non_coprime_a() -> None:
    with pytest.raises(ValueError):
        controlled_mult_mod(5, 15, 4)


def test_circuit_size() -> None:
    qc = order_finding_circuit(7, 15)
    assert qc.num_qubits == 12
    assert qc.num_clbits == 8


@pytest.mark.parametrize(
    ("a", "n"), [(2, 15), (4, 15), (7, 15), (8, 15), (11, 15), (13, 15), (2, 21), (3, 35)]
)
def test_find_order_matches_classical_order(a: int, n: int) -> None:
    assert find_order(a, n, seed=1) == classical_order(a, n)


def test_order_from_counts_combines_partial_denominators() -> None:
    # 2 has order 6 mod 21. Readings of 1/2 and 1/3 each give only a divisor
    # of 6, so the answer has to come from lcm(2, 3).
    counts = {format(512, "010b"): 5, format(341, "010b"): 3}
    assert order_from_counts(counts, 2, 21) == 6


def test_order_from_counts_returns_none_on_zero_phase() -> None:
    assert order_from_counts({"00000000": 16}, 7, 15) is None


@pytest.mark.parametrize(("n", "a"), [(15, 7), (15, 2), (15, 13), (21, 2)])
def test_factor_uses_order_finding(n: int, a: int) -> None:
    result = factor(n, a=a, seed=0)
    p, q = result.factors
    assert result.method == "order finding"
    assert p * q == n and 1 < p < n
    assert result.order == classical_order(a, n)


@pytest.mark.parametrize("n", [15, 21, 33, 35])
def test_factor_with_random_a(n: int) -> None:
    p, q = factor(n, seed=3).factors
    assert p * q == n and 1 < p < n


def test_classical_shortcuts() -> None:
    assert factor(22).method == "even"
    assert factor(49).factors == (7, 7)
    assert factor(27).method == "perfect power"


@pytest.mark.parametrize("n", [2, 3, 13, 97, 1 << 8])
def test_rejects_bad_input(n: int) -> None:
    with pytest.raises(ValueError):
        factor(n)


def test_odd_order_raises_after_retries() -> None:
    # 4^3 = 64 = 1 (mod 21), so r = 3 is odd and a=4 can never work.
    assert classical_order(4, 21) == 3
    with pytest.raises(RuntimeError):
        factor(21, a=4, max_attempts=2, seed=0)


def test_gcd_shortcut_when_a_shares_a_factor() -> None:
    result = factor(15, a=6)
    assert result.method == "gcd"
    assert math.prod(result.factors) == 15
