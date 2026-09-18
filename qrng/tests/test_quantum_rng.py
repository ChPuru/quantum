from collections import Counter

import pytest

from src.quantum_rng import random_bits, random_int


def test_length_and_alphabet() -> None:
    bits = random_bits(100, seed=1)
    assert len(bits) == 100
    assert set(bits) <= {"0", "1"}


def test_seed_makes_it_reproducible() -> None:
    assert random_bits(64, seed=5) == random_bits(64, seed=5)
    assert random_bits(64, seed=5) != random_bits(64, seed=6)


def test_roughly_balanced() -> None:
    bits = random_bits(20000, seed=2)
    assert bits.count("1") / len(bits) == pytest.approx(0.5, abs=0.015)


def test_random_int_is_uniform_over_range() -> None:
    rolls = Counter(random_int(1, 6, seed=s) for s in range(3000))
    assert set(rolls) == {1, 2, 3, 4, 5, 6}
    for count in rolls.values():
        assert count == pytest.approx(500, abs=80)


def test_random_int_edges() -> None:
    assert random_int(7, 7, seed=0) == 7
    assert 0 <= random_int(0, 1, seed=0) <= 1
    assert -10 <= random_int(-10, 10, seed=3) <= 10


@pytest.mark.parametrize("n", [0, -3])
def test_rejects_non_positive_length(n: int) -> None:
    with pytest.raises(ValueError):
        random_bits(n)


def test_rejects_empty_range() -> None:
    with pytest.raises(ValueError):
        random_int(5, 4)
