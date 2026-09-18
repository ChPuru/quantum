"""Adiabatic quantum annealing for MaxCut, simulated with an exact statevector.

The anneal follows H(s) = (1 - s) * H_driver + s * H_problem for s from 0 to 1:

    H_driver  = -sum_i X_i         ground state |+>^n, easy to prepare
    H_problem =  sum_ij w_ij Z_i Z_j   ground states are the maximum cuts

If s moves slowly enough compared with the energy gap, the state stays close
to the instantaneous ground state and ends on a maximum cut (adiabatic
theorem). A fast sweep leaves population in excited states.

This is a classical simulation of the Schrodinger equation, not a run on an
annealer. It uses Qiskit only to build the Pauli operators, and it is limited
to about 16 nodes.
"""

from __future__ import annotations

import itertools
from collections.abc import Hashable
from dataclasses import dataclass

import networkx as nx
import numpy as np
from qiskit.quantum_info import SparsePauliOp
from scipy.sparse.linalg import expm_multiply

MAX_NODES = 16


@dataclass(frozen=True)
class AnnealResult:
    probabilities: np.ndarray  # over basis states, index bit i = node i
    best_assignment: dict[Hashable, int]  # most likely final state
    best_cut: float
    max_cut: float  # found by brute force
    success_probability: float  # total probability on maximum cuts


def _edges(graph: nx.Graph) -> list[tuple[int, int, float]]:
    index = {node: i for i, node in enumerate(graph.nodes)}
    return [(index[u], index[v], float(d.get("weight", 1.0))) for u, v, d in graph.edges(data=True)]


def problem_hamiltonian(graph: nx.Graph) -> SparsePauliOp:
    n = graph.number_of_nodes()
    terms = [("ZZ", [i, j], w) for i, j, w in _edges(graph)]
    return SparsePauliOp.from_sparse_list(terms, num_qubits=n).simplify()


def driver_hamiltonian(n: int) -> SparsePauliOp:
    return SparsePauliOp.from_sparse_list([("X", [i], -1.0) for i in range(n)], num_qubits=n)


def cut_values(graph: nx.Graph) -> np.ndarray:
    """Cut value of every basis state, indexed the same way as the statevector."""
    n = graph.number_of_nodes()
    index = np.arange(2**n)
    cuts = np.zeros(2**n)
    for i, j, w in _edges(graph):
        cuts += w * (((index >> i) ^ (index >> j)) & 1)
    return cuts


def anneal(graph: nx.Graph, total_time: float = 10.0, steps: int = 200) -> AnnealResult:
    """Evolve |+>^n under H(s) with a linear schedule, in `steps` equal slices."""
    n = graph.number_of_nodes()
    if n < 2 or graph.number_of_edges() == 0:
        raise ValueError("graph needs at least two nodes and one edge")
    if n > MAX_NODES:
        raise ValueError(f"{n} nodes is too many to simulate exactly (max {MAX_NODES})")

    h_driver = driver_hamiltonian(n).to_matrix(sparse=True)
    h_problem = problem_hamiltonian(graph).to_matrix(sparse=True)

    state = np.full(2**n, 2 ** (-n / 2), dtype=complex)
    dt = total_time / steps
    for k in range(steps):
        s = (k + 0.5) / steps  # midpoint of the slice
        h = (1 - s) * h_driver + s * h_problem
        state = expm_multiply(-1j * dt * h, state)

    probabilities = np.abs(state) ** 2
    cuts = cut_values(graph)
    max_cut = cuts.max()
    best_index = int(np.argmax(probabilities))
    nodes = list(graph.nodes)

    return AnnealResult(
        probabilities=probabilities,
        best_assignment={node: (best_index >> i) & 1 for i, node in enumerate(nodes)},
        best_cut=float(cuts[best_index]),
        max_cut=float(max_cut),
        success_probability=float(probabilities[np.isclose(cuts, max_cut)].sum()),
    )


def brute_force_maxcut(graph: nx.Graph) -> float:
    n = graph.number_of_nodes()
    edges = _edges(graph)
    return max(
        sum(w for i, j, w in edges if bits[i] != bits[j])
        for bits in itertools.product((0, 1), repeat=n)
    )
