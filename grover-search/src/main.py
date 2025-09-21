# src/main.py

import argparse
from src.grover import GroverSearch

def main():
    parser = argparse.ArgumentParser(description="Grover's Quantum Search Algorithm")
    parser.add_argument(
        "--qubits",
        type=int,
        required=True,
        help="Number of qubits (size of the search space is 2^qubits)."
    )
    parser.add_argument(
        "--marked_item",
        type=str,
        required=True,
        help="The binary string to search for."
    )
    args = parser.parse_args()

    try:
        print("--- Grover's Search Simulation ---")
        print(f"Searching for '{args.marked_item}' in a {args.qubits}-qubit space.")
        
        grover = GroverSearch(num_qubits=args.qubits, marked_item=args.marked_item)
        num_iterations = grover.build_circuit()
        
        print(f"Optimal number of iterations: {num_iterations}")
        
        results = grover.run(shots=1024)
        found_item = results['most_frequent_result']
        counts = results['counts']
        
        print("\n--- Simulation Results ---")
        print(f"Most frequent result: {found_item}")
        
        success_prob = counts.get(args.marked_item, 0) / 1024
        print(f"Probability of finding '{args.marked_item}': {success_prob:.2%}")

        if found_item == args.marked_item:
            print("\nResult: SUCCESS - The marked item was found with high probability.")
        else:
            print("\nResult: FAILURE - The marked item was not the most frequent outcome.")
        print("---------------------------------")
        # Optional: print the circuit
        # print("\n--- Quantum Circuit ---")
        # print(grover.circuit.draw(output='text'))

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()