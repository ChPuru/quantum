# src/shors.py

import math
import random
from fractions import Fraction
import numpy as np
# REMOVE 'assemble' from this import
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer, AerSimulator
from qiskit.circuit.library import QFT

class Shor:
    """
    Encapsulates the logic for Shor's integer factorization algorithm.
    """

    def __init__(self, N: int):
        if not isinstance(N, int) or N <= 1:
            raise ValueError("N must be an integer greater than 1.")
        self.N = N
        self.backend = Aer.get_backend('aer_simulator')

    def _classical_pre_checks(self):
        """Perform classical checks to find factors more easily."""
        if self.N % 2 == 0:
            return 2, self.N // 2
        
        # This check is not part of Shor's but can find factors for non-prime composites
        for i in range(3, int(math.sqrt(self.N)) + 1, 2):
             if self.N % i == 0:
                return i, self.N // i
        
        return None, None

    def _get_period(self, a: int):
        """Finds the period 'r' of the function f(x) = a^x mod N using a quantum circuit."""
        n_count = self.N.bit_length()
        
        qc = QuantumCircuit(n_count * 2, n_count)
        qc.h(range(n_count))
        qc.x(n_count * 2 - 1)

        for q in range(n_count):
            qc.append(self._c_amodN(a, 2**q, self.N, n_count), 
                      [q] + list(range(n_count, n_count * 2)))

        qc.append(QFT(n_count, do_swaps=False).inverse(), range(n_count))
        qc.measure(range(n_count), range(n_count))
        
        # Modern execution workflow
        t_qc = transpile(qc, self.backend)
        result = self.backend.run(t_qc, shots=1, memory=True).result()
        readings = result.get_memory()
        phase = int(readings[0], 2) / (2**n_count)

        frac = Fraction(phase).limit_denominator(self.N)
        r = frac.denominator
        return r

    def run(self):
        """
        Executes the full Shor's algorithm.
        """
        p, q = self._classical_pre_checks()
        if p:
            return {"status": "SUCCESS", "factors": (p, q), "method": "Classical Check"}

        while True:
            a = random.randint(2, self.N - 1)
            gcd_val = math.gcd(a, self.N)
            if gcd_val > 1:
                return {"status": "SUCCESS", "factors": (gcd_val, self.N // gcd_val), "method": "Lucky Guess"}

            print(f"Attempting period-finding for a = {a}...")
            r = self._get_period(a)

            if r is None or r % 2 != 0:
                print(f"Period r={r} is odd or invalid. Trying a new 'a'.")
                continue
            
            factor1 = math.gcd(a**(r//2) + 1, self.N)
            factor2 = math.gcd(a**(r//2) - 1, self.N)

            if factor1 != 1 and factor1 != self.N:
                return {"status": "SUCCESS", "factors": (factor1, self.N // factor1), "method": "Shor's Algorithm"}
            if factor2 != 1 and factor2 != self.N:
                return {"status": "SUCCESS", "factors": (factor2, self.N // factor2), "method": "Shor's Algorithm"}
            
            print("Found trivial factors. Trying a new 'a'.")

    # Helper methods for building the modular exponentiation circuit
    def _c_amodN(self, a, power, N, n_count):
        """Controlled multiplication by a mod N."""
        U = QuantumCircuit(n_count)
        for _ in range(power):
            U.append(self._amodN(a, N, n_count), range(n_count))
        
        U = U.to_gate()
        U.name = f"{a}^{power} mod {N}"
        c_U = U.control()
        return c_U

    def _amodN(self, a, N, n_count):
        """Circuit for multiplication by a mod N."""
        if N != 15:
            raise NotImplementedError("This demo only supports N=15 for the modular exponentiation circuit.")
        
        qc = QuantumCircuit(n_count)
        if a == 2 or a == 8: # 2^1=2, 2^2=4, 2^3=8, 2^4=1 -> period 4
            qc.swap(0, 1)
            qc.swap(1, 2)
            qc.swap(2, 3)
        elif a == 4 or a == 11: # 4^1=4, 4^2=1 -> period 2
            qc.swap(0, 2)
            qc.swap(1, 3)
        elif a == 7 or a == 13: # 7^1=7, 7^2=4, 7^3=13, 7^4=1 -> period 4
            qc.swap(0, 1)
            qc.swap(1, 2)
            qc.swap(2, 3)
            qc.x(range(4))
        
        gate = qc.to_gate()
        gate.name = f"*{a} mod {N}"
        return gate