"""Meyer's quantum penny flip, from D. A. Meyer, Phys. Rev. Lett. 82, 1052 (1999).

A coin starts heads up (|0>). Q moves, Picard moves, Q moves again, then the
coin is checked. Picard may only flip it (X) or leave it (I). Q wins on heads.

A classical Q who flips at random wins half the games, and so does any
classical Q against a Picard who flips at random. A quantum Q plays H twice:
the first H puts the coin in |+>, which Picard's X leaves unchanged, and the
second H turns it back into |0>. Q wins every game.
"""

from __future__ import annotations

from collections import Counter

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

Q_MOVES = ("I", "X", "H")
PICARD_MOVES = ("I", "X")


def game_circuit(q_first: str, picard: str, q_second: str, measure: bool = True) -> QuantumCircuit:
    for move, allowed in ((q_first, Q_MOVES), (picard, PICARD_MOVES), (q_second, Q_MOVES)):
        if move not in allowed:
            raise ValueError(f"{move!r} is not one of {allowed}")
    qc = QuantumCircuit(1, 1 if measure else 0)
    for move in (q_first, picard, q_second):
        if move == "X":
            qc.x(0)
        elif move == "H":
            qc.h(0)
        qc.barrier()
    if measure:
        qc.measure(0, 0)
    return qc


def heads_probability(q_first: str, picard: str, q_second: str) -> float:
    """Exact probability that Q wins, from the statevector."""
    state = Statevector(game_circuit(q_first, picard, q_second, measure=False))
    return float(state.probabilities()[0])


def payoff_table() -> dict[tuple[str, str], dict[str, float]]:
    """P(heads) for every pure Q strategy (first, second) against each Picard move."""
    return {
        (a, b): {p: heads_probability(a, p, b) for p in PICARD_MOVES}
        for a in Q_MOVES
        for b in Q_MOVES
    }


def play(n_games: int, q_strategy: str, seed: int | None = None) -> float:
    """Q's win rate over n games against a Picard who flips with probability 1/2.

    q_strategy is "quantum" (H, H) or "classical" (I or X on each turn, at random).
    """
    if q_strategy not in ("quantum", "classical"):
        raise ValueError("q_strategy must be 'quantum' or 'classical'")
    rng = np.random.default_rng(seed)

    picard = rng.choice(PICARD_MOVES, size=n_games)
    if q_strategy == "quantum":
        first = second = np.full(n_games, "H")
    else:
        first = rng.choice(("I", "X"), size=n_games)
        second = rng.choice(("I", "X"), size=n_games)

    # Group identical games so each distinct circuit runs once with many shots.
    games = Counter(zip(first, picard, second, strict=True))
    backend = AerSimulator()
    heads = 0
    for (a, p, b), count in games.items():
        counts = (
            backend.run(game_circuit(a, p, b), shots=count, seed_simulator=int(rng.integers(2**31)))
            .result()
            .get_counts()
        )
        heads += counts.get("0", 0)
    return heads / n_games
