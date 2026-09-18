import networkx as nx
import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from src.qaoa_maxcut import (
    brute_force_maxcut,
    cost_hamiltonian,
    cut_value,
    qaoa_circuit,
    solve,
)


def square() -> nx.Graph:
    return nx.Graph([(0, 1), (1, 2), (2, 3), (3, 0)])


def test_hamiltonian_energy_matches_cut_value() -> None:
    graph = nx.Graph([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    h = cost_hamiltonian(graph)
    total = graph.number_of_edges()
    for index in range(16):
        bits = [(index >> q) & 1 for q in range(4)]
        energy = Statevector.from_int(index, 16).expectation_value(h).real
        assert (total - energy) / 2 == pytest.approx(cut_value(graph, bits))


def test_circuit_parameters() -> None:
    qc = qaoa_circuit(square(), reps=3)
    assert qc.num_parameters == 6
    assert qc.count_ops()["rzz"] == 12


def test_square_graph() -> None:
    result = solve(square(), reps=2, seed=0)
    assert result.cut_value == 4
    assert sorted(map(sorted, result.partition)) == [[0, 2], [1, 3]]
    assert result.best_probability > 0.5


def test_five_node_graph_matches_brute_force() -> None:
    graph = nx.Graph([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 4)])
    result = solve(graph, reps=2, seed=1)
    assert result.cut_value == brute_force_maxcut(graph) == 6


def test_weighted_graph() -> None:
    graph = nx.Graph()
    graph.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 1.0), (0, 2, 1.0)])
    result = solve(graph, reps=2, seed=2)
    # Node 0 and node 1 must end up on different sides to cut the heavy edge.
    assert result.assignment[0] != result.assignment[1]
    assert result.cut_value == brute_force_maxcut(graph) == 6.0


def test_string_node_labels() -> None:
    graph = nx.Graph([("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")])
    result = solve(graph, reps=1, seed=4)
    assert result.cut_value == 4
    assert result.assignment["a"] == result.assignment["c"]


def test_expected_cut_is_bounded() -> None:
    result = solve(square(), reps=1, seed=5)
    assert 2 <= result.expected_cut <= 4
    assert np.all(np.isfinite(result.parameters))


def test_rejects_graph_without_edges() -> None:
    graph = nx.Graph()
    graph.add_nodes_from([0, 1])
    with pytest.raises(ValueError):
        solve(graph)
