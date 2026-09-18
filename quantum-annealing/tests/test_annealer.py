import networkx as nx
import numpy as np
import pytest

from src.annealer import anneal, brute_force_maxcut, cut_values, problem_hamiltonian


def square() -> nx.Graph:
    return nx.Graph([(0, 1), (1, 2), (2, 3), (3, 0)])


def test_cut_values_match_problem_hamiltonian() -> None:
    graph = nx.Graph([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    energies = np.real(np.diag(problem_hamiltonian(graph).to_matrix()))
    # For unit weights, cut = (edges - energy) / 2.
    np.testing.assert_allclose(cut_values(graph), (5 - energies) / 2)


def test_square_ends_on_maximum_cut() -> None:
    result = anneal(square())
    assert result.best_cut == result.max_cut == 4
    assert result.success_probability > 0.95
    assert result.best_assignment[0] == result.best_assignment[2]
    assert result.best_assignment[0] != result.best_assignment[1]


def test_probabilities_are_normalised() -> None:
    assert anneal(square(), total_time=3).probabilities.sum() == pytest.approx(1.0)


def test_slower_anneal_does_better() -> None:
    graph = nx.Graph([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 4)])
    fast = anneal(graph, total_time=0.5).success_probability
    slow = anneal(graph, total_time=20).success_probability
    assert fast < 0.6 < 0.9 < slow


def test_triangle_and_weights() -> None:
    triangle = nx.Graph([(0, 1), (1, 2), (2, 0)])
    assert anneal(triangle).best_cut == 2

    weighted = nx.Graph()
    weighted.add_weighted_edges_from([(0, 1, 3.0), (1, 2, 1.0), (0, 2, 1.0)])
    result = anneal(weighted, total_time=20)
    assert result.best_cut == brute_force_maxcut(weighted) == 4.0


def test_node_labels_do_not_have_to_start_at_zero() -> None:
    graph = nx.Graph([(1, 2), (2, 3), (3, 4), (4, 1)])
    result = anneal(graph)
    assert set(result.best_assignment) == {1, 2, 3, 4}
    assert result.best_cut == 4


def test_rejects_bad_graphs() -> None:
    with pytest.raises(ValueError):
        anneal(nx.empty_graph(3))
    with pytest.raises(ValueError):
        anneal(nx.path_graph(17))
