# src/main.py

from src.quantum_validator import QuantumValidator
from src.blockchain import Blockchain, Block

def mine_block(blockchain: Blockchain, data: str):
    """
    Finds a valid nonce for the new block (mining) and adds it to the chain.
    """
    print(f"\nMining a new block for data: '{data}'...")
    latest_block = blockchain.get_latest_block()
    nonce = 0
    while True:
        new_block = Block(
            index=latest_block.index + 1,
            data=data,
            previous_hash=latest_block.hash,
            nonce=nonce
        )
        if blockchain.validator.validate_block(new_block):
            blockchain.chain.append(new_block)
            print(f"  -> Success! Found a valid block with nonce = {nonce}.")
            break
        else:
            nonce += 1

def main():
    NUM_QUBITS = 4
    TARGET_STATE = '1' * NUM_QUBITS

    print("--- Quantum Blockchain Prototype ---")
    
    validator = QuantumValidator(num_qubits=NUM_QUBITS, target_state=TARGET_STATE)
    q_blockchain = Blockchain(quantum_validator=validator)
    print(f"Blockchain initialized. Validation requires measuring '{TARGET_STATE}'.")

    # 2. Mine some valid blocks. This is now guaranteed to work.
    mine_block(q_blockchain, "Transaction Data 1")
    mine_block(q_blockchain, "Transaction Data 2")

    # 3. Demonstrate tampering (This will now work because chain[1] exists)
    print("\n--- Demonstrating Tampering ---")
    print("Original data of Block 1:", q_blockchain.chain[1].data)
    
    q_blockchain.chain[1].data = "Tampered Data"
    print("Tampered data of Block 1:", q_blockchain.chain[1].data)
    
    print("\nRe-validating the tampered block with the quantum validator...")
    is_tampered_block_valid = validator.validate_block(q_blockchain.chain[1])
    
    if not is_tampered_block_valid:
        print("  -> As expected, the tampered block FAILED quantum validation.")
    else:
        print("  -> The tampered block unexpectedly passed validation.")
        
    print("\nFinal chain integrity check:", q_blockchain.is_chain_valid())
    print("---------------------------------")

if __name__ == "__main__":
    main()