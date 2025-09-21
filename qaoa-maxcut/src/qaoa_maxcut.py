# src/qaoa_maxcut.py

import networkx as nx
from qiskit_aer.primitives import Sampler
# Corrected imports for the new qiskit_algorithms package
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.converters import QuadraticProgramToQubo

class QAOAMaxCut:
    """
    Encapsulates the logic for solving the Max-Cut problem using QAOA.
    """

    def __init__(self, graph: nx.Graph):
        if not isinstance(graph, nx.Graph):
            raise TypeError("Input must be a valid networkx Graph object.")
        self.graph = graph
        self.qubit_op = None
        self.offset = 0

    def _create_qubit_operator(self):
        """
        Converts the Max-Cut problem into a qubit Hamiltonian (Ising model)
        using the Qiskit Optimization library.
        """
        max_cut_problem = Maxcut(self.graph)
        qp = max_cut_problem.to_quadratic_program()
        conv = QuadraticProgramToQubo()
        qubo = conv.convert(qp)
        self.qubit_op, self.offset = qubo.to_ising()

    def solve(self, reps: int = 1):
        """
        Sets up and runs the QAOA algorithm.
        """
        if self.qubit_op is None:
            self._create_qubit_operator()

        sampler = Sampler()
        optimizer = COBYLA()

        # Instantiate the QAOA algorithm
        qaoa = QAOA(
            sampler=sampler,
            optimizer=optimizer,
            reps=reps
        )

        result = qaoa.compute_minimum_eigenvalue(self.qubit_op)
        
        solution_bitstring = result.optimal_point
        
        max_cut_instance = Maxcut(self.graph)
        solution_sets = max_cut_instance.get_graph_solution(solution_bitstring)
        num_edges_cut = max_cut_instance.get_max_cut_value(solution_bitstring)

        return {
            "solution_sets": solution_sets,
            "num_edges_cut": num_edges_cut,
            "solution_bitstring": "".join([str(int(i)) for i in solution_bitstring]),
            "optimal_parameters": result.optimal_parameters
        }