# src/qnn_classifier.py

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from qiskit_aer.primitives import Sampler
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit_algorithms.optimizers import COBYLA
from qiskit_machine_learning.algorithms import VQC
# SamplerQNN is no longer needed here as VQC builds it internally

class QNNClassifier:
    """
    A Quantum Neural Network (QNN) classifier using the Variational Quantum Classifier (VQC)
    algorithm for binary classification.
    """

    def __init__(self, num_qubits: int, feature_dim: int):
        self.num_qubits = num_qubits
        self.feature_dim = feature_dim
        # We no longer pre-build the QNN. VQC will handle it.
        self.vqc = None

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Trains the VQC model using the classical optimizer.
        """
        # Define the components of the QNN directly here.
        
        # 1. Feature Map (Encoder)
        feature_map = ZZFeatureMap(feature_dimension=self.feature_dim, reps=2)

        # 2. Ansatz (Variational Form)
        ansatz = RealAmplitudes(num_qubits=self.num_qubits, reps=3)

        # 3. Instantiate the VQC algorithm using the modern, component-based constructor
        self.vqc = VQC(
            sampler=Sampler(),
            feature_map=feature_map,
            ansatz=ansatz,
            optimizer=COBYLA(maxiter=50),
            initial_point=np.random.rand(ansatz.num_parameters) * 0.1
        )

        print("Starting VQC training...")
        self.vqc.fit(X_train, y_train)
        print("Training complete.")

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray):
        """
        Evaluates the trained model's accuracy.
        """
        if self.vqc is None:
            raise RuntimeError("Model must be trained before evaluation.")

        y_pred = self.vqc.predict(X_test)
        accuracy = np.mean(y_pred == y_test)
        
        return accuracy

def load_and_preprocess_data(num_samples: int = 100):
    """
    Generates a simple synthetic dataset for binary classification.
    """
    X0 = np.random.normal(loc=[-0.5, -0.5], scale=0.3, size=(num_samples // 2, 2))
    y0 = np.zeros(num_samples // 2)
    X1 = np.random.normal(loc=[0.5, 0.5], scale=0.3, size=(num_samples // 2, 2))
    y1 = np.ones(num_samples // 2)

    X = np.vstack((X0, X1))
    y = np.hstack((y0, y1))

    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.3, random_state=42
    )
    
    return X_train, X_test, y_train, y_test