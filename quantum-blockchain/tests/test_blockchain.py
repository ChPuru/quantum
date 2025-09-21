# tests/test_blockchain.py

import unittest
from src.quantum_validator import QuantumValidator
from src.blockchain import Blockchain, Block

class TestQuantumBlockchain(unittest.TestCase):

    def setUp(self):
        self.validator = QuantumValidator(num_qubits=4, target_state='1111')
        self.blockchain = Blockchain(self.validator)

    def test_block_creation(self):
        """Test that a block is created with the correct attributes."""
        latest_block = self.blockchain.get_latest_block()
        new_block = Block(latest_block.index + 1, "Test Data", latest_block.hash)
        self.assertEqual(new_block.index, 1)
        self.assertEqual(new_block.data, "Test Data")
        self.assertEqual(new_block.previous_hash, latest_block.hash)

    def test_validation_failure(self):
        """
        Test that a block with arbitrary data (which is very unlikely to be valid) fails validation.
        """
        # This block is statistically almost certain to be invalid.
        is_added = self.blockchain.add_block("This data will almost certainly not produce the target state")
        self.assertFalse(is_added)

    def test_chain_tampering(self):
        """Test that the classical chain integrity check detects tampering."""
        # We need to find a valid block first to add to the chain.
        # For testing, we can bypass the quantum check to add a block.
        latest_block = self.blockchain.get_latest_block()
        new_block = Block(latest_block.index + 1, "Valid Data", latest_block.hash)
        self.blockchain.chain.append(new_block)
        
        # Now, tamper with the block
        self.blockchain.chain[1].data = "Tampered Data"
        
        # The chain should now be invalid
        self.assertFalse(self.blockchain.is_chain_valid())

if __name__ == '__main__':
    unittest.main()