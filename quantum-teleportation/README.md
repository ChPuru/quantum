# Quantum teleportation

Teleports a random one-qubit state from Alice's qubit q0 to Bob's qubit q2 using a shared Bell pair and two classical bits, simulated with Qiskit Aer. Bob's X and Z corrections use dynamic circuits (`if_test`).

## Run

```bash
pip install -r requirements.txt
python -m src.main --seed 4 --draw
python -m pytest
```

```
$ python -m src.main --seed 4
Alice measured  z=0 x=1
message Bloch vector   (+0.662, -0.076, +0.746)
Bob's Bloch vector     (+0.662, -0.076, +0.746)
fidelity               1.000000
```

## Checking the result

Alice's measurement collapses the three-qubit state into one of four branches. `teleport` takes Bob's qubit with a partial trace over q0 and q1 and compares it with the message by state fidelity, so the check works in every branch. The tests run enough seeds to hit all four.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.

## Credits

The circuit layout follows the teleportation chapter of the [Qiskit Textbook](https://github.com/Qiskit/textbook) (Apache-2.0). See NOTICE in the repository root.
