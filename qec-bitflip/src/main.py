# src/main.py

import numpy as np
from qiskit.quantum_info import random_statevector
from src.bit_flip_code import BitFlipCode

def main():
    try:
        print("--- 3-Qubit Bit-Flip Code Simulation ---")
        
        # 1. Create a random initial state for the logical qubit
        initial_state = random_statevector(2)
        print(f"Initial logical state: {np.round(initial_state.data, 3)}")

        # 2. Initialize and run the simulation
        qec_sim = BitFlipCode(initial_state=initial_state)
        results = qec_sim.run_and_verify()

        # THIS IS THE CORRECTED PART: We no longer print a final state,
        # as our verification now compares the full encoded states.
        print("-" * 40)

        if results['success']:
            print("Result: SUCCESS! The state was recovered correctly.")
        else:
            print("Result: FAILURE! The final state does not match the initial state.")
        
        print("----------------------------------------")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()