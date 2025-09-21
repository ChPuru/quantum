# src/teleportation.py

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import random_statevector, Statevector
from qiskit_aer import AerSimulator

class Teleportation:
    """
    Encapsulates the logic for the Quantum Teleportation protocol.
    """

    def __init__(self):
        self.qr = QuantumRegister(3, name="q")
        self.crz = ClassicalRegister(1, name="crz")
        self.crx = ClassicalRegister(1, name="crx")
        self.circuit = QuantumCircuit(self.qr, self.crz, self.crx)
        self.backend = AerSimulator()

    def _create_bell_pair(self):
        """Creates an entangled Bell pair between q1 and q2."""
        self.circuit.h(1)
        self.circuit.cx(1, 2)
        self.circuit.barrier()

    def _alice_operations(self):
        """Alice performs operations on her message qubit (q0) and her entangled qubit (q1)."""
        self.circuit.cx(0, 1)
        self.circuit.h(0)
        self.circuit.barrier()

    def _alice_measures(self):
        """Alice measures her two qubits and stores the results in classical registers."""
        self.circuit.measure(0, self.crz)
        self.circuit.measure(1, self.crx)
        self.circuit.barrier()

    def _bob_operations(self):
        """Bob applies gates to his qubit (q2) based on the classical bits Alice sent him."""
        with self.circuit.if_test((self.crx, 1)):
            self.circuit.x(2)
        with self.circuit.if_test((self.crz, 1)):
            self.circuit.z(2)

    def build_circuit(self):
        """Builds the full teleportation circuit."""
        self._create_bell_pair()
        self._alice_operations()
        self._alice_measures()
        self._bob_operations()
        return self.circuit

    def run_and_verify(self, initial_state_vec: Statevector):
        """
        Runs the simulation and verifies the teleportation.
        """
        sim_circuit = self.circuit.copy()
        sim_circuit.save_statevector()
        
        result = self.backend.run(sim_circuit).result()
        final_statevector = result.get_statevector()

        # The statevector is ordered |q2 q1 q0>.
        # We extract the amplitudes corresponding to |00> for Alice's qubits.
        bob_vector_data = [final_statevector.data[0], final_statevector.data[4]]
        
        # The Statevector constructor automatically normalizes the data.
        bob_final_state = Statevector(bob_vector_data) # <-- This is the corrected line

        # Compare the initial and final states
        success = initial_state_vec.equiv(bob_final_state)

        return {
            "initial_state": initial_state_vec.data,
            "final_state": bob_final_state.data,
            "success": success
        }

def create_random_message_state():
    """Creates a random single-qubit statevector."""
    return random_statevector(2, seed=np.random.randint(1000))