# Toy blockchain with a circuit-based proof of work

A small hash-linked chain where a block counts as valid when a 4-qubit circuit built from its SHA-256 hash has |1111⟩ as its single most likely outcome. Mining tries nonces until that happens.

## Run

```bash
pip install -r requirements.txt
python -m src.main
python -m pytest
```

```
$ python -m src.main
a block is valid when its circuit favours |1111>

block 1  nonce 73   P(1111) = 0.208  'alice pays bob 5'
block 2  nonce 166  P(1111) = 0.183  'bob pays carol 2'
block 3  nonce 59   P(1111) = 0.316  'carol pays alice 1'

chain valid         True
edited block 1 ...
chain valid         False
```

Nonces change between runs because blocks carry the current time.

## How it works

Each hex digit of the hash adds one gate, cycling over the qubits: 0-3 give H, 4-7 give X, 8-b give a CX from the neighbouring qubit, c-f give RZ(digit·π/8). The validator computes exact outcome probabilities from the statevector, so the same block always gets the same verdict. `Blockchain.is_valid` checks every link and re-runs the validator on every block.

## What this is not

This is a toy. The circuit adds no security over SHA-256 alone: a 4-qubit circuit is trivial to simulate on a laptop, which is what this code does, and running it on quantum hardware would only add noise. It exists as practice at turning data into circuits.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2. The simulator package is not needed here.
