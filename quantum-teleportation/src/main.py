import argparse

from src.teleportation import bloch_vector, random_message, teleport, teleportation_circuit


def fmt(vec: tuple[float, float, float]) -> str:
    return "(" + ", ".join(f"{v:+.3f}" for v in vec) + ")"


def main() -> None:
    parser = argparse.ArgumentParser(description="Teleport a random one-qubit state.")
    parser.add_argument("--seed", type=int, help="seed for the message and the simulator")
    parser.add_argument("--draw", action="store_true", help="print the circuit")
    args = parser.parse_args()

    message = random_message(args.seed)
    result = teleport(message, seed=args.seed)

    print(f"Alice measured  z={result.z_bit} x={result.x_bit}")
    print(f"message Bloch vector   {fmt(bloch_vector(message))}")
    print(f"Bob's Bloch vector     {fmt(bloch_vector(result.received))}")
    print(f"fidelity               {result.fidelity:.6f}")

    if args.draw:
        print(teleportation_circuit(message).draw(output="text"))


if __name__ == "__main__":
    main()
