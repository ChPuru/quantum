# tests/test_bb84.py

import unittest
import numpy as np
from src.bb84 import BB84, Z_BASIS, X_BASIS

class TestBB84(unittest.TestCase):
    
    def test_init(self):
        """Test that the BB84 class initializes correctly."""
        protocol = BB84(num_bits=10)
        self.assertEqual(protocol.num_bits, 10)
        self.assertEqual(len(protocol.alice_bits), 10)
        self.assertEqual(len(protocol.alice_bases), 10)
        self.assertEqual(len(protocol.bob_bases), 10)

    def test_sifting(self):
        """Test the key sifting logic."""
        protocol = BB84(num_bits=8)
        # Manually set bases for a predictable outcome
        protocol.alice_bases = np.array([Z_BASIS, X_BASIS, Z_BASIS, X_BASIS, Z_BASIS, X_BASIS, Z_BASIS, X_BASIS])
        protocol.bob_bases   = np.array([Z_BASIS, Z_BASIS, X_BASIS, X_BASIS, Z_BASIS, X_BASIS, X_BASIS, Z_BASIS])
        # Matches should be at indices 0, 3, 4, 5
        
        bob_mock_bits = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        
        alice_sifted, bob_sifted = protocol._sift_keys(bob_mock_bits)
        
        self.assertEqual(len(alice_sifted), 4)
        self.assertEqual(len(bob_sifted), 4)
        
        expected_alice_sifted = protocol.alice_bits[[0, 3, 4, 5]]
        np.testing.assert_array_equal(alice_sifted, expected_alice_sifted)

    def test_simulation_no_eavesdropper(self):
        """Test a full simulation without Eve, expecting a 0% error rate."""
        protocol = BB84(num_bits=100)
        results = protocol.simulate(eavesdrop=False)
        self.assertFalse(results['eavesdropper_detected'])
        self.assertEqual(results['error_rate'], 0.0)

    def test_simulation_with_eavesdropper(self):
        """Test a full simulation with Eve, expecting a non-zero error rate."""
        # Run multiple times as the random nature might occasionally result in 0 errors
        for _ in range(5):
            protocol = BB84(num_bits=200)
            results = protocol.simulate(eavesdrop=True)
            # With an eavesdropper, the error rate should be around 25% on the sifted key
            # We check if it's > 0, which is a strong indicator.
            if results['error_rate'] > 0:
                self.assertTrue(results['eavesdropper_detected'])
                return
        # If after 5 runs we still get 0 error, something might be wrong, but it's statistically unlikely.
        # For a robust test, one might check if the error rate is > 0 over many runs.
        # For this test, we'll raise an assertion failure if it's always 0.
        self.fail("Eavesdropper simulation consistently resulted in 0% error rate, which is highly unlikely.")

if __name__ == '__main__':
    unittest.main()