# tests/test_shors.py

import unittest
from src.shors import Shor

class TestShor(unittest.TestCase):

    def test_factor_15(self):
        """
        Tests that Shor's algorithm can successfully factor N=15.
        This may take a moment to run.
        """
        shor_instance = Shor(N=15)
        results = shor_instance.run()

        self.assertEqual(results['status'], 'SUCCESS')
        p, q = results['factors']
        self.assertEqual(p * q, 15)
        # The factors of 15 are 3 and 5.
        self.assertIn(p, [3, 5])
        self.assertIn(q, [3, 5])

if __name__ == '__main__':
    unittest.main()