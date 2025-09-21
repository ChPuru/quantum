# src/quantum_rng.py

from qiskit import QuantumCircuit
from qiskit_aer import Aer # Corrected import for Aer
import numpy as np

class QuantumRNG:
    """
    A Quantum Random Number Generator.

    This class uses the principles of quantum mechanics to generate true random numbers.
    It leverages the Qiskit framework to create a quantum circuit, apply a Hadamard
    gate to induce superposition, and then measure the state of the qubits to
    produce random bits.
    """

    def __init__(self, backend_name: str = 'aer_simulator'):
        """
        Initializes the QuantumRNG.

        Args:
            backend_name (str): The name of the Qiskit Aer backend to use.
                                Defaults to 'aer_simulator'.
        """
        # The 'qasm_simulator' is legacy, 'aer_simulator' is the modern standard
        self.backend = Aer.get_backend(backend_name)
        self.circuit = None

    def _build_circuit(self, num_bits: int):
        """
        Builds the quantum circuit for generating random bits.

        Args:
            num_bits (int): The number of random bits to generate.
        """
        self.circuit = QuantumCircuit(num_bits, num_bits)
        # Apply Hadamard gate to all qubits to put them in a superposition
        self.circuit.h(range(num_bits))
        # Measure all qubits
        self.circuit.measure(range(num_bits), range(num_bits))

    def generate_bits(self, num_bits: int) -> str:
        """
        Generates a string of random bits.

        Args:
            num_bits (int): The number of random bits to generate.

        Returns:
            str: A string of random bits.
        """
        if not isinstance(num_bits, int) or num_bits <= 0:
            raise ValueError("Number of bits must be a positive integer.")

        self._build_circuit(num_bits)
        
        # The modern way to run a job, replacing the deprecated execute()
        job = self.backend.run(self.circuit, shots=1, memory=True)
        result = job.result()
        
        # Using memory=True gives us a list of the results, e.g., ['10110']
        # This is more direct than getting counts for a single shot.
        return result.get_memory(self.circuit)[0]

    def get_circuit_diagram(self):
        """
        Returns a string representation of the quantum circuit diagram.

        Returns:
            str: The circuit diagram.
        """
        if self.circuit is None:
            return "Circuit has not been built yet. Call generate_bits() first."
        return str(self.circuit.draw(output='text'))