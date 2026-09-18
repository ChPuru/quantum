from src.blockchain import Blockchain
from src.quantum_validator import QuantumValidator


def main() -> None:
    validator = QuantumValidator(num_qubits=4)
    chain = Blockchain(validator)
    print(f"a block is valid when its circuit favours |{validator.target}>\n")

    for data in ["alice pays bob 5", "bob pays carol 2", "carol pays alice 1"]:
        block = chain.mine(data)
        p = validator.probabilities(block.compute_hash())[validator.target]
        print(
            f"block {block.index}  nonce {block.nonce:<4} P({validator.target}) = {p:.3f}  {data!r}"
        )

    print(f"\nchain valid         {chain.is_valid()}")
    chain.chain[1].data = "alice pays bob 500"
    print("edited block 1 ...")
    print(f"chain valid         {chain.is_valid()}")


if __name__ == "__main__":
    main()
