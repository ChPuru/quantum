# BB84 quantum key distribution

Simulates BB84 between Alice and Bob, optionally with an eavesdropper who intercepts each qubit, measures it and sends on what she measured.

## Run

```bash
pip install -r requirements.txt
python -m src.main --bits 64 --seed 1
python -m src.main --bits 64 --seed 1 --eavesdrop
python -m pytest
```

```
$ python -m src.main --seed 1
sent                64 qubits
same basis          38
revealed for check  19
QBER                0.0% (abort above 11%)
key (19 bits)       1110111111001011010
keys match          True
```

With `--eavesdrop` the error rate on the checked bits jumps to about 25% and the run aborts.

## How it works

1. Alice picks random bits and bases. Z basis sends |0⟩ or |1⟩, X basis sends |+⟩ or |−⟩.
2. Bob measures each qubit in a random basis. Where the bases match he reads Alice's bit; elsewhere he gets a coin flip.
3. They announce bases, keep the matching positions, and reveal half of those to estimate the quantum bit error rate (QBER).
4. They abort above 11%, roughly the highest QBER at which one-way post-processing can still produce a secret key.

An intercept-resend attacker guesses the wrong basis half the time, and then Bob reads the wrong bit half of those times: 25% errors.

The qubits never interact and every gate is a Clifford gate, so the code packs them into 64-qubit circuits and runs them on Aer's stabilizer simulator in one job.

## Limits

This is a model of the protocol, not a secure implementation: randomness comes from NumPy's seeded generator, there is no channel noise, and the key skips error correction and privacy amplification.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.
