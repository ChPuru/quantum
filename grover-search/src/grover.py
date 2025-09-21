# src/grover.py

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.circuit.library import MCXGate

class GroverSearch:
    """
    Encapsulates the logic for Grover's unstructured search algorithm.
    """

    def __init__(self, num_qubits: int, marked_item: str):
        if len(marked_item) != num_qubits or not all(c in '01' for c in marked_item):
            raise ValueError("Marked item must be a binary string of length num_qubits.")
        
        self.num_qubits = num_qubits
        self.marked_item = marked_item
        self.circuit = QuantumCircuit(num_qubits)
        self.backend = AerSimulator()

    def _build_oracle(self):
        """
        Constructs the oracle operator that marks the desired item.
        """
        oracle_qc = QuantumCircuit(self.num_qubits, name="Oracle")
        zero_indices = [i for i, bit in enumerate(self.marked_item) if bit == '0']
        
        if zero_indices:
            oracle_qc.x(zero_indices)
            
        oracle_qc.h(self.num_qubits - 1)
        num_controls = self.num_qubits - 1
        oracle_qc.append(MCXGate(num_controls), list(range(self.num_qubits)))
        oracle_qc.h(self.num_qubits - 1)
        
        if zero_indices:
            oracle_qc.x(zero_indices)
            
        return oracle_qc.to_gate()

    def _build_diffuser(self):
        """
        Constructs the diffuser (amplitude amplification) operator.
        """
        diffuser_qc = QuantumCircuit(self.num_qubits, name="Diffuser")
        
        diffuser_qc.h(range(self.num_qubits))
        diffuser_qc.x(range(self.num_qubits))
        
        diffuser_qc.h(self.num_qubits - 1)
        num_controls = self.num_qubits - 1
        diffuser_qc.append(MCXGate(num_controls), list(range(self.num_qubits)))
        diffuser_qc.h(self.num_qubits - 1)
        
        diffuser_qc.x(range(self.num_qubits))
        diffuser_qc.h(range(self.num_qubits))
        
        return diffuser_qc.to_gate()

    def build_circuit(self):
        """
        Builds the full Grover search circuit.
        """
        self.circuit.h(range(self.num_qubits))
        self.circuit.barrier()

        oracle = self._build_oracle()
        diffuser = self._build_diffuser()
        
        num_iterations = int(np.floor(np.pi / 4 * np.sqrt(2**self.num_qubits)))
        
        for _ in range(num_iterations):
            self.circuit.append(oracle, range(self.num_qubits))
            self.circuit.append(diffuser, range(self.num_qubits))
            self.circuit.barrier()
            
        self.circuit.measure_all()
        return num_iterations

    def run(self, shots: int = 1024):
        """
        Runs the simulation and returns the results.
        """
        if not self.circuit.clbits:
            raise RuntimeError("Circuit has not been built yet. Call build_circuit() first.")
        
        # Decompose the circuit before running
        decomposed_circuit = self.circuit.decompose()
            
        job = self.backend.run(decomposed_circuit, shots=shots) # Run the decomposed version
        result = job.result()
        counts = result.get_counts()
        
        most_frequent = max(counts, key=counts.get)
        
        return {
            "counts": counts,
            "most_frequent_result": most_frequent
        }