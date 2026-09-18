import pytest

from src.quantum_penny_flip import game_circuit, heads_probability, payoff_table, play


@pytest.mark.parametrize("picard", ["I", "X"])
def test_hadamard_strategy_always_wins(picard: str) -> None:
    assert heads_probability("H", picard, "H") == pytest.approx(1.0)


def test_classical_moves_are_deterministic() -> None:
    assert heads_probability("I", "I", "I") == pytest.approx(1.0)
    assert heads_probability("I", "X", "I") == pytest.approx(0.0)
    assert heads_probability("X", "X", "I") == pytest.approx(1.0)


def test_no_classical_q_strategy_beats_a_random_picard() -> None:
    table = payoff_table()
    for (a, b), row in table.items():
        if "H" not in (a, b):
            assert (row["I"] + row["X"]) / 2 == pytest.approx(0.5)


def test_half_quantum_strategies_do_not_help() -> None:
    # One H without the other leaves the coin in a 50/50 state.
    assert heads_probability("H", "X", "I") == pytest.approx(0.5)
    assert heads_probability("I", "I", "H") == pytest.approx(0.5)


def test_simulated_win_rates() -> None:
    assert play(4000, "quantum", seed=1) == 1.0
    assert play(4000, "classical", seed=1) == pytest.approx(0.5, abs=0.03)


def test_rejects_quantum_moves_for_picard() -> None:
    with pytest.raises(ValueError):
        game_circuit("H", "H", "H")
    with pytest.raises(ValueError):
        play(10, "cheating")
