# src/bb84_key_exchange.py

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import hashlib

class BB84KeyExchange:
    """
    Simulates the BB84 protocol to generate a secure shared key.
    """
    def __init__(self):
        self.backend = AerSimulator()

    def _encode_qubits(self, bits, bases):
        qubits = []
        for i in range(len(bits)):
            qc = QuantumCircuit(1, 1)
            if bits[i] == 1: qc.x(0)
            if bases[i] == 'X': qc.h(0)
            qubits.append(qc)
        return qubits

    def _measure_qubits(self, qubits, bases):
        measured_bits = []
        for i in range(len(qubits)):
            qc = qubits[i]
            if bases[i] == 'X': qc.h(0)
            qc.measure(0, 0)
            result = self.backend.run(qc, shots=1, memory=True).result()
            measured_bits.append(int(result.get_memory()[0]))
        return np.array(measured_bits)

    def generate_secure_key(self, key_length_bytes: int = 32):
        """
        Runs the BB84 protocol until a key of the desired length is generated.

        Returns:
            bytes: A secure key of the specified byte length.
        """
        print("Starting Quantum Key Distribution (BB84)...")
        final_key_bits = []
        
        # We need key_length_bytes * 8 bits.
        # BB84 is inefficient, so we start with a much larger number of initial bits.
        required_bits = key_length_bytes * 8
        
        while len(final_key_bits) < required_bits:
            # Estimate the number of bits needed. On average, 1/4 of bits are kept.
            # We'll use a factor of 5 to be safe.
            num_initial_bits = (required_bits - len(final_key_bits)) * 5
            
            alice_bits = np.random.randint(2, size=num_initial_bits)
            alice_bases = np.random.choice(['Z', 'X'], size=num_initial_bits)
            bob_bases = np.random.choice(['Z', 'X'], size=num_initial_bits)
            
            alice_qubits = self._encode_qubits(alice_bits, alice_bases)
            bob_measured_bits = self._measure_qubits(alice_qubits, bob_bases)
            
            matching_indices = np.where(alice_bases == bob_bases)[0]
            
            sifted_key = alice_bits[matching_indices]
            final_key_bits.extend(sifted_key)

        # Truncate to the exact required length
        final_key_bits = final_key_bits[:required_bits]
        
        # Convert the list of bits to a byte string
        key_byte_string = int("".join(map(str, final_key_bits)), 2).to_bytes(key_length_bytes, 'big')
        
        print("  -> Secure key generated successfully.")
        return key_byte_string