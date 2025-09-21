# tests/test_qnn_classifier.py

import unittest
from src.qnn_classifier import QNNClassifier, load_and_preprocess_data

class TestQNNClassifier(unittest.TestCase):

    def test_training_and_accuracy(self):
        """
        Tests that the VQC model can train and achieve a reasonable accuracy
        on the simple synthetic dataset.
        """
        NUM_QUBITS = 2
        FEATURE_DIM = 2
        
        X_train, X_test, y_train, y_test = load_and_preprocess_data(num_samples=50)
        
        classifier = QNNClassifier(num_qubits=NUM_QUBITS, feature_dim=FEATURE_DIM)
        
        # Test training completion
        try:
            classifier.train(X_train, y_train)
        except Exception as e:
            self.fail(f"Training failed: {e}")

        # Test accuracy (should be high for this simple data)
        accuracy = classifier.evaluate(X_test, y_test)
        self.assertGreaterEqual(accuracy, 0.80, "Accuracy should be at least 80% for this simple dataset.")

if __name__ == '__main__':
    unittest.main()