# src/main.py

import argparse
from src.bb84 import BB84

def main():
    parser = argparse.ArgumentParser(description="BB84 Quantum Key Distribution Simulation")
    parser.add_argument(
        "--bits",
        type=int,
        default=30,
        help="The number of bits in the initial key exchange."
    )
    parser.add_argument(
        "--eavesdrop",
        action="store_true",
        help="Simulate with an eavesdropper present."
    )
    args = parser.parse_args()

    try:
        protocol = BB84(num_bits=args.bits)
        results = protocol.simulate(eavesdrop=args.eavesdrop)

        print("--- BB84 Simulation Results ---")
        print(f"Eavesdropper Present: {args.eavesdrop}")
        print("-" * 31)
        print(f"Initial Key Length:    {results['initial_key_length']}")
        print(f"Sifted Key Length:     {results['sifted_key_length']} (approx. 50%)")
        print(f"Final Shared Key Length: {results['final_key_length']} (approx. 25%)")
        print(f"Quantum Bit Error Rate (QBER): {results['error_rate']:.2%}")
        print("-" * 31)

        if results['eavesdropper_detected']:
            print("\nResult: EAVESDROPPER DETECTED! Key exchange aborted.")
        else:
            print("\nResult: Key exchange successful.")
            print(f"Final Shared Secret Key: {results['final_key']}")
        print("---------------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()