import numpy as np
import pytest

from src.qnn_classifier import QNNClassifier, make_dataset


def test_dataset_split_and_scaling() -> None:
    data = make_dataset(num_samples=100, test_size=0.3, seed=0)
    assert data.x_train.shape == (70, 2)
    assert data.x_test.shape == (30, 2)
    assert data.x_train.min() == pytest.approx(0.0)
    assert data.x_train.max() == pytest.approx(1.0)
    assert data.x_test.min() >= 0.0 and data.x_test.max() <= 1.0
    # stratified split keeps the classes balanced
    assert np.bincount(data.y_train).tolist() == [35, 35]


def test_dataset_is_reproducible() -> None:
    a, b = make_dataset(seed=5), make_dataset(seed=5)
    np.testing.assert_array_equal(a.x_train, b.x_train)


def test_predict_before_fit_raises() -> None:
    with pytest.raises(RuntimeError):
        QNNClassifier().predict(np.zeros((1, 2)))


def test_learns_blobs() -> None:
    data = make_dataset(num_samples=100, seed=1)
    model = QNNClassifier(seed=1).fit(data.x_train, data.y_train)
    assert model.score(data.x_train, data.y_train) >= 0.85
    assert model.score(data.x_test, data.y_test) >= 0.85
    assert model.loss_history[-1] < model.loss_history[0]
