# src/annealer.py

import numpy as np
import networkx as nx
from scipy.linalg import expm

class QuantumAnnealer:
    """
    A classical simulator for a quantum annealing process to solve Max-Cut.
    """

    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.num_nodes = len(graph.nodes)
        self.H_problem = self._create_problem_hamiltonian()
        self.H_driver = self._create_driver_hamiltonian()

    def _create_problem_hamiltonian(self):
        """Creates the Ising Hamiltonian for the Max-Cut problem."""
        dim = 2**self.num_nodes
        hamiltonian = np.zeros((dim, dim))
        
        # The Ising model energy is -sum(J_ij * s_i * s_j)
        # For Max-Cut, J_ij = -1 if there is an edge, 0 otherwise.
        # We represent spins s_i as Pauli Z matrices.
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                if self.graph.has_edge(i, j):
                    # J_ij = -1, so we add Z_i * Z_j to the Hamiltonian
                    hamiltonian += self._get_pauli_product('Z', i, 'Z', j)
        return hamiltonian

    def _create_driver_hamiltonian(self):
        """Creates the transverse field (driver) Hamiltonian."""
        dim = 2**self.num_nodes
        hamiltonian = np.zeros((dim, dim))
        # The driver is the sum of Pauli X matrices for each qubit.
        for i in range(self.num_nodes):
            hamiltonian += self._get_pauli_product('X', i)
        return -hamiltonian # Conventionally negative

    def _get_pauli_product(self, p1, i1, p2=None, i2=None):
        """Helper to construct the matrix for a product of Pauli operators."""
        pauli_map = {
            'I': np.eye(2),
            'X': np.array([[0, 1], [1, 0]]),
            'Z': np.array([[1, 0], [0, -1]])
        }
        
        op_list = [pauli_map['I']] * self.num_nodes
        op_list[i1] = pauli_map[p1]
        if p2 is not None:
            op_list[i2] = pauli_map[p2]
            
        # Use Kronecker product to build the full matrix
        full_op = op_list[0]
        for op in op_list[1:]:
            full_op = np.kron(full_op, op)
        return full_op

    def anneal(self, total_time: float = 5.0, time_steps: int = 100):
        """
        Simulates the quantum annealing process.
        """
        # 1. Initial state: Uniform superposition of all possible states
        # This is the ground state of the driver Hamiltonian.
        initial_state = np.ones(2**self.num_nodes) / np.sqrt(2**self.num_nodes)
        current_state = initial_state.astype(complex)
        
        dt = total_time / time_steps

        # 2. Annealing schedule: A(t) and B(t)
        # A(t) controls the driver, starts high and goes to zero.
        # B(t) controls the problem, starts at zero and goes high.
        for t_step in range(time_steps + 1):
            s = t_step / time_steps
            A_s = 1 - s
            B_s = s
            
            # 3. Construct the time-dependent Hamiltonian
            H_t = A_s * self.H_driver + B_s * self.H_problem
            
            # 4. Evolve the state using the Schrödinger equation: psi(t+dt) = e^(-i*H*dt) * psi(t)
            U_t = expm(-1j * H_t * dt)
            current_state = U_t @ current_state

        # 5. Measure the final state
        probabilities = np.abs(current_state)**2
        most_likely_state_index = np.argmax(probabilities)
        
        # Convert the index to a binary string (spin configuration)
        solution_str = format(most_likely_state_index, f'0{self.num_nodes}b')
        return solution_str

    def get_max_cut_solution(self, solution_str: str):
        """Calculates the Max-Cut value for a given solution string."""
        cut_count = 0
        for i, j in self.graph.edges():
            if solution_str[i] != solution_str[j]:
                cut_count += 1
        
        partition = (
            [node for node, bit in enumerate(solution_str) if bit == '0'],
            [node for node, bit in enumerate(solution_str) if bit == '1']
        )
        return cut_count, partition