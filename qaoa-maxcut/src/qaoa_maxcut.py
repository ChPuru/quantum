"""MaxCut with QAOA, built from Qiskit primitives and SciPy's COBYLA.

For a graph with edge weights w_ij, a cut assigns each node a side z_i = +-1
and scores sum w_ij * (1 - z_i z_j) / 2. Maximising the cut is the same as
minimising H = sum w_ij Z_i Z_j, so QAOA minimises <H> and then samples
bitstrings from the optimised circuit.
"""

from __future__ import annotations

import itertools
from collections.abc import Hashable
from dataclasses import dataclass

import networkx as nx
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp
from scipy.optimize import minimize


@dataclass(frozen=True)
class MaxCutResult:
    cut_value: float
    partition: tuple[set[Hashable], set[Hashable]]
    assignment: dict[Hashable, int]  # node -> 0 or 1
    best_probability: float  # share of shots that landed on a maximum cut
    expected_cut: float  # cut value averaged over the optimised state
    parameters: np.ndarray  # gamma_1..gamma_p, beta_1..beta_p


def _edges(graph: nx.Graph) -> list[tuple[int, int, float]]:
    index = {node: i for i, node in enumerate(graph.nodes)}
    return [(index[u], index[v], float(d.get("weight", 1.0))) for u, v, d in graph.edges(data=True)]


def cost_hamiltonian(graph: nx.Graph) -> SparsePauliOp:
    """H = sum w_ij Z_i Z_j, with qubit i standing for the i-th node of graph.nodes."""
    terms = [("ZZ", [i, j], w) for i, j, w in _edges(graph)]
    return SparsePauliOp.from_sparse_list(terms, num_qubits=graph.number_of_nodes()).simplify()


def cut_value(graph: nx.Graph, bits: list[int]) -> float:
    """Total weight of edges whose endpoints sit on different sides. bits[i] is node i's side."""
    return sum(w for i, j, w in _edges(graph) if bits[i] != bits[j])


def brute_force_maxcut(graph: nx.Graph) -> float:
    n = graph.number_of_nodes()
    return max(cut_value(graph, list(bits)) for bits in itertools.product((0, 1), repeat=n))


def qaoa_circuit(graph: nx.Graph, reps: int) -> QuantumCircuit:
    """p layers of exp(-i gamma H) followed by the X mixer exp(-i beta sum X)."""
    n = graph.number_of_nodes()
    gammas = ParameterVector("gamma", reps)
    betas = ParameterVector("beta", reps)

    qc = QuantumCircuit(n)
    qc.h(range(n))
    for layer in range(reps):
        for i, j, w in _edges(graph):
            qc.rzz(2 * gammas[layer] * w, i, j)
        qc.rx(2 * betas[layer], range(n))
    return qc


def solve(
    graph: nx.Graph,
    reps: int = 2,
    restarts: int = 5,
    shots: int = 2048,
    seed: int | None = None,
) -> MaxCutResult:
    """Optimise the QAOA angles, then sample and keep the best cut seen.

    COBYLA gets stuck in local minima of the angle landscape, so it runs from
    `restarts` random starting points and keeps the lowest <H>.
    """
    if graph.number_of_nodes() < 2 or graph.number_of_edges() == 0:
        raise ValueError("graph needs at least two nodes and one edge")

    rng = np.random.default_rng(seed)
    hamiltonian = cost_hamiltonian(graph)
    circuit = qaoa_circuit(graph, reps)
    estimator = StatevectorEstimator()

    def energy(params: np.ndarray) -> float:
        result = estimator.run([(circuit, hamiltonian, params)]).result()
        return float(result[0].data.evs)

    best = None
    for _ in range(restarts):
        start = np.concatenate([rng.uniform(0, np.pi, reps), rng.uniform(0, np.pi / 2, reps)])
        res = minimize(energy, start, method="COBYLA", options={"maxiter": 300})
        if best is None or res.fun < best.fun:
            best = res
    assert best is not None

    measured = circuit.assign_parameters(best.x)
    measured.measure_all()
    sampler = StatevectorSampler(seed=int(rng.integers(2**31)))
    counts = sampler.run([measured], shots=shots).result()[0].data.meas.get_counts()

    # Counts keys put qubit 0 on the right, so reverse to get node order.
    scored = {key: cut_value(graph, [int(b) for b in key[::-1]]) for key in counts}
    best_key = max(scored, key=scored.__getitem__)
    best_cut = scored[best_key]

    nodes = list(graph.nodes)
    bits = [int(b) for b in best_key[::-1]]
    assignment = dict(zip(nodes, bits, strict=True))
    total_weight = sum(w for _, _, w in _edges(graph))

    return MaxCutResult(
        cut_value=best_cut,
        partition=(
            {node for node, side in assignment.items() if side == 0},
            {node for node, side in assignment.items() if side == 1},
        ),
        assignment=assignment,
        best_probability=sum(c for k, c in counts.items() if scored[k] == best_cut) / shots,
        expected_cut=(total_weight - best.fun) / 2,
        parameters=best.x,
    )
