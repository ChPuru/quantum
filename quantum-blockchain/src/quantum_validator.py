# src/quantum_validator.py

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

class QuantumValidator:
    """
    Validates blocks using a quantum circuit generated from the block's hash.
    """
    def __init__(self, num_qubits: int, target_state: str):
        if len(target_state) != num_qubits or not all(c in '01' for c in target_state):
            raise ValueError("Target state must be a binary string of length num_qubits.")
        
        self.num_qubits = num_qubits
        self.target_state = target_state
        self.backend = AerSimulator()

    def _generate_circuit_from_hash(self, block_hash: str):
        """
        Creates a unique quantum circuit based on the block's hash.
        This acts as the "quantum fingerprint."
        """
        qc = QuantumCircuit(self.num_qubits)
        
        # Use the hash characters to build the circuit
        for i, char in enumerate(block_hash):
            qubit_index = i % self.num_qubits
            control_qubit = (i + 1) % self.num_qubits
            
            # Apply a gate based on the character
            if char in '0123':
                qc.h(qubit_index)
            elif char in '4567':
                qc.x(qubit_index)
            elif char in '89ab':
                qc.cx(control_qubit, qubit_index)
            elif char in 'cdef':
                qc.rz(ord(char) * 3.14 / 16, qubit_index)
        
        qc.measure_all()
        return qc

    def validate_block(self, block) -> bool:
        """
        Runs the validation circuit and checks if the outcome is the target state.
        """
        block_hash = block.calculate_hash()
        validation_circuit = self._generate_circuit_from_hash(block_hash)
        
        # Simulate the circuit
        result = self.backend.run(validation_circuit, shots=100).result()
        counts = result.get_counts()
        
        # Find the most frequent measurement outcome
        most_frequent_outcome = max(counts, key=counts.get)
        
        print(f"  - Quantum Validation: Most frequent outcome is '{most_frequent_outcome}'.")
        
        # Check if the outcome matches our target
        return most_frequent_outcome == self.target_state