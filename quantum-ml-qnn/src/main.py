# src/main.py

import numpy as np
from src.qnn_classifier import QNNClassifier, load_and_preprocess_data

def main():
    # Define parameters
    NUM_QUBITS = 2  # Number of features/qubits
    FEATURE_DIM = 2 # Dimension of the input data
    NUM_SAMPLES = 100

    try:
        print("--- Quantum Neural Network Classifier ---")
        
        # 1. Load and prepare data
        X_train, X_test, y_train, y_test = load_and_preprocess_data(NUM_SAMPLES)
        print(f"Data loaded: {len(X_train)} training samples, {len(X_test)} test samples.")

        # 2. Initialize and train the classifier
        classifier = QNNClassifier(num_qubits=NUM_QUBITS, feature_dim=FEATURE_DIM)
        classifier.train(X_train, y_train)

        # 3. Evaluate the model
        accuracy = classifier.evaluate(X_test, y_test)

        print("\n--- Results ---")
        print(f"Test Accuracy: {accuracy:.2%}")
        print("-----------------")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()