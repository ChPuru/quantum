# src/main.py

import argparse
from src.quantum_rng import QuantumRNG

def main():
    """
    Main function to run the Quantum Random Number Generator from the command line.
    """
    parser = argparse.ArgumentParser(description="Quantum Random Number Generator")
    parser.add_argument(
        "--bits",
        type=int,
        default=8,
        help="The number of random bits to generate."
    )
    args = parser.parse_args()

    try:
        rng = QuantumRNG()
        random_bits = rng.generate_bits(args.bits)

        print("--- Quantum Random Number Generator ---")
        print(f"Generated {args.bits} random bits: {random_bits}")
        print("\n--- Quantum Circuit Diagram ---")
        print(rng.get_circuit_diagram())
        print("-----------------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()