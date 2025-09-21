# src/main.py

import argparse
from src.shors import Shor

def main():
    parser = argparse.ArgumentParser(description="Shor's Algorithm for Integer Factorization")
    parser.add_argument(
        "--number",
        type=int,
        default=15,
        help="The integer to factor. This demo is optimized for N=15."
    )
    args = parser.parse_args()

    if args.number != 15:
        print("Warning: This demo's modular exponentiation circuit is hardcoded for N=15.")
        print("Running with other numbers is not supported by this simplified implementation.")
        return

    try:
        print(f"--- Running Shor's Algorithm to Factor N={args.number} ---")
        
        shor_instance = Shor(N=args.number)
        results = shor_instance.run()

        print("\n--- Results ---")
        print(f"Status: {results['status']}")
        print(f"Method: {results['method']}")
        if results['status'] == 'SUCCESS':
            p, q = results['factors']
            print(f"Found factors: {p} and {q}")
            print(f"Verification: {p} * {q} = {p*q}")
        print("---------------")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()