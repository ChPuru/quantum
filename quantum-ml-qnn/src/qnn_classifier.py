"""Variational quantum classifier (VQC) for 2-D binary data.

Features go through a ZZ feature map, a RealAmplitudes ansatz is trained with
COBYLA, and the sampled parity of the output bitstring gives the class. The
dataset is two overlapping Gaussian blobs, small enough to train in seconds on
a statevector sampler.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from qiskit.circuit.library import real_amplitudes, zz_feature_map
from qiskit.primitives import StatevectorSampler
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


@dataclass
class Dataset:
    x_train: np.ndarray
    x_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray


def make_dataset(num_samples: int = 100, test_size: float = 0.3, seed: int = 0) -> Dataset:
    """Two Gaussian blobs centred at (-0.5, -0.5) and (0.5, 0.5).

    The scaler is fit on the training split only, so no test information leaks
    into the features.
    """
    rng = np.random.default_rng(seed)
    half = num_samples // 2
    x = np.vstack(
        [
            rng.normal(loc=-0.5, scale=0.3, size=(half, 2)),
            rng.normal(loc=0.5, scale=0.3, size=(num_samples - half, 2)),
        ]
    )
    y = np.array([0] * half + [1] * (num_samples - half))

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=seed, stratify=y
    )
    scaler = MinMaxScaler(feature_range=(0, 1)).fit(x_train)
    return Dataset(
        x_train=scaler.transform(x_train),
        x_test=np.clip(scaler.transform(x_test), 0, 1),
        y_train=y_train,
        y_test=y_test,
    )


@dataclass
class QNNClassifier:
    num_features: int = 2
    feature_reps: int = 2
    ansatz_reps: int = 3
    maxiter: int = 60
    seed: int = 0
    loss_history: list[float] = field(default_factory=list, init=False)
    _vqc: VQC | None = field(default=None, init=False, repr=False)

    def fit(self, x: np.ndarray, y: np.ndarray) -> QNNClassifier:
        feature_map = zz_feature_map(self.num_features, reps=self.feature_reps)
        ansatz = real_amplitudes(self.num_features, reps=self.ansatz_reps)
        rng = np.random.default_rng(self.seed)
        self.loss_history.clear()

        self._vqc = VQC(
            sampler=StatevectorSampler(seed=self.seed),
            feature_map=feature_map,
            ansatz=ansatz,
            optimizer=COBYLA(maxiter=self.maxiter),
            # Small random start avoids the flat region around all-zero angles.
            initial_point=rng.uniform(-0.1, 0.1, ansatz.num_parameters),
            callback=lambda _weights, loss: self.loss_history.append(float(loss)),
        )
        self._vqc.fit(x, y)
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        return self._fitted().predict(x)

    def score(self, x: np.ndarray, y: np.ndarray) -> float:
        return float(self._fitted().score(x, y))

    def _fitted(self) -> VQC:
        if self._vqc is None:
            raise RuntimeError("call fit() before predict() or score()")
        return self._vqc
