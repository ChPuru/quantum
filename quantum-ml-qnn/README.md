# Variational quantum classifier

Trains a two-qubit variational quantum classifier (`VQC` from Qiskit Machine Learning) on synthetic 2-D data: two Gaussian blobs centred at (-0.5, -0.5) and (0.5, 0.5), scaled to [0, 1].

| Part | Choice |
| --- | --- |
| Feature map | `zz_feature_map`, 2 reps |
| Ansatz | `real_amplitudes`, 3 reps, 8 trainable angles |
| Optimizer | COBYLA, 60 iterations |
| Sampler | `StatevectorSampler`, 1024 shots |
| Class label | parity of the measured bitstring |

With the default seed it reaches about 97% accuracy on both the training and the test split, in roughly 10 seconds.

## Run

```bash
pip install -r requirements.txt
python -m src.main
python -m pytest
```

```
$ python -m src.main
70 training samples, 30 test samples
final training loss  0.3380
train accuracy       97.1%
test accuracy        96.7%
```

The notebook plots the data, the loss curve and the decision boundary.

Tested with Python 3.12 on Qiskit 2.1.1 and 2.5.2 with Qiskit Machine Learning 0.9.1.
