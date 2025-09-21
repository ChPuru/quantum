# src/bb84.py

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Define the two bases
Z_BASIS = 'Z'  # Computational basis |0>, |1>
X_BASIS = 'X'  # Hadamard basis |+>, |->

class BB84:
    """
    Encapsulates the logic for the BB84 Quantum Key Distribution protocol.
    """

    def __init__(self, num_bits: int):
        if not isinstance(num_bits, int) or num_bits <= 0:
            raise ValueError("Number of bits must be a positive integer.")
        self.num_bits = num_bits
        self.alice_bits = np.random.randint(2, size=num_bits)
        self.alice_bases = np.random.choice([Z_BASIS, X_BASIS], size=num_bits)
        self.bob_bases = np.random.choice([Z_BASIS, X_BASIS], size=num_bits)
        self.backend = AerSimulator()

    def _encode_qubits(self):
        """Alice encodes her bits onto qubits based on her chosen bases."""
        qubits = []
        for i in range(self.num_bits):
            qc = QuantumCircuit(1, 1)
            # Encode bit 1
            if self.alice_bits[i] == 1:
                qc.x(0)
            # Apply basis transformation
            if self.alice_bases[i] == X_BASIS:
                qc.h(0)
            qubits.append(qc)
        return qubits

    def _measure_qubits(self, qubits, bases):
        """Measures a list of qubits using a corresponding list of bases."""
        measured_bits = []
        for i in range(len(qubits)):
            qc = qubits[i]
            # Apply basis transformation for measurement
            if bases[i] == X_BASIS:
                qc.h(0)
            qc.measure(0, 0)

            # Simulate the circuit
            job = self.backend.run(qc, shots=1, memory=True)
            result = job.result()
            measured_bit = int(result.get_memory(qc)[0])
            measured_bits.append(measured_bit)
        return np.array(measured_bits)

    def _sift_keys(self, bob_measured_bits):
        """Alice and Bob compare bases and keep bits where bases matched."""
        matching_bases_indices = np.where(self.alice_bases == self.bob_bases)[0]
        
        alice_sifted_key = self.alice_bits[matching_bases_indices]
        bob_sifted_key = bob_measured_bits[matching_bases_indices]
        
        return alice_sifted_key, bob_sifted_key

    def _check_for_eavesdropper(self, alice_key, bob_key, sample_size=0.5):
        """
        Alice and Bob compare a sample of their keys to detect Eve.
        Returns the final key and the error rate.
        """
        if len(alice_key) == 0:
            return np.array([]), 0.0

        num_samples = int(len(alice_key) * sample_size)
        if num_samples == 0 and len(alice_key) > 0:
            num_samples = 1 # Ensure at least one sample for small keys

        sample_indices = np.random.choice(len(alice_key), num_samples, replace=False)
        
        alice_sample = alice_key[sample_indices]
        bob_sample = bob_key[sample_indices]

        # Calculate error rate
        errors = np.sum(alice_sample != bob_sample)
        error_rate = errors / num_samples if num_samples > 0 else 0.0

        # The final key is what's left after removing the public samples
        final_key_indices = np.setdiff1d(np.arange(len(alice_key)), sample_indices)
        final_key = alice_key[final_key_indices]

        return final_key, error_rate

    def simulate(self, eavesdrop: bool = False):
        """
        Runs the full BB84 simulation.

        Args:
            eavesdrop (bool): If True, an eavesdropper (Eve) will intercept
                              and measure the qubits.

        Returns:
            dict: A dictionary containing the results of the simulation.
        """
        # 1. Alice encodes her qubits
        alice_qubits = self._encode_qubits()

        # 2. Eve intercepts (optional)
        if eavesdrop:
            eve_bases = np.random.choice([Z_BASIS, X_BASIS], size=self.num_bits)
            eve_measured_bits = self._measure_qubits(alice_qubits, eve_bases)
            # Eve resends new qubits based on her measurements
            bob_received_qubits = self._re_encode_for_eve(eve_measured_bits, eve_bases)
        else:
            bob_received_qubits = alice_qubits

        # 3. Bob measures the qubits he receives
        bob_measured_bits = self._measure_qubits(bob_received_qubits, self.bob_bases)

        # 4. Alice and Bob sift their keys
        alice_sifted_key, bob_sifted_key = self._sift_keys(bob_measured_bits)

        # 5. Alice and Bob check for an eavesdropper
        final_key, error_rate = self._check_for_eavesdropper(alice_sifted_key, bob_sifted_key)

        return {
            "initial_key_length": self.num_bits,
            "sifted_key_length": len(alice_sifted_key),
            "final_key_length": len(final_key),
            "error_rate": error_rate,
            "eavesdropper_detected": error_rate > 0.1, # Threshold can be adjusted
            "final_key": ''.join(map(str, final_key))
        }

    def _re_encode_for_eve(self, bits, bases):
        """Helper for Eve to create new qubits based on her measurements."""
        qubits = []
        for i in range(len(bits)):
            qc = QuantumCircuit(1, 1)
            if bits[i] == 1:
                qc.x(0)
            if bases[i] == X_BASIS:
                qc.h(0)
            qubits.append(qc)
        return qubits