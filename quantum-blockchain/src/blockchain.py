# src/blockchain.py

import hashlib
import time
from .quantum_validator import QuantumValidator

class Block:
    """A single block in the blockchain."""
    def __init__(self, index, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = time.time()
        self.data = str(data)
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculates the SHA-256 hash of the block's contents."""
        block_string = str(self.index) + str(self.timestamp) + self.data + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    """The main blockchain structure."""
    def __init__(self, quantum_validator: QuantumValidator):
        self.chain = [self._create_genesis_block()]
        self.validator = quantum_validator

    def _create_genesis_block(self):
        """Creates the very first block in the chain."""
        return Block(0, "Genesis Block", "0")

    def get_latest_block(self):
        """Returns the most recent block in the chain."""
        return self.chain[-1]

    # THIS METHOD WAS MISSING AND HAS BEEN ADDED BACK
    def is_chain_valid(self):
        """Checks the integrity of the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Check if the block's hash is still correct
            if current_block.hash != current_block.calculate_hash():
                return False
            # Check if the block points to the previous block's hash
            if current_block.previous_hash != previous_block.hash:
                return False
        return True