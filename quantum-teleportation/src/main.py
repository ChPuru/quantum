# src/main.py

import numpy as np
from qiskit import transpile
from src.teleportation import Teleportation, create_random_message_state

def main():
    try:
        print("--- Quantum Teleportation Simulation ---")

        # 1. Create a random quantum state for Alice's message
        message_state = create_random_message_state()
        print(f"Alice's initial message state: {np.round(message_state.data, 3)}")

        # 2. Initialize the message qubit with this state
        teleporter = Teleportation()
        teleporter.circuit.initialize(message_state, 0)
        teleporter.circuit.barrier()

        # 3. Build the rest of the teleportation circuit
        teleporter.build_circuit()

        # 4. Run the simulation and verify the result
        results = teleporter.run_and_verify(message_state)

        print(f"Bob's final received state:    {np.round(results['final_state'], 3)}")
        print("-" * 40)

        if results['success']:
            print("Result: SUCCESS! The quantum state was teleported correctly.")
        else:
            print("Result: FAILURE! The states do not match.")
        
        print("\n--- Quantum Circuit ---")
        # We need to transpile to see the 'if_test' conditions properly
        # The AerSimulator can handle if_test directly, but drawing needs transpilation.
        t_circ = transpile(teleporter.circuit, teleporter.backend)
        print(t_circ.draw(output='text'))
        print("----------------------------------------")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()