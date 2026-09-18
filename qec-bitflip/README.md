# Three-qubit bit-flip code

Encodes one qubit into three, measures two parity checks with ancilla qubits, and fixes a single bit flip with feed-forward (`if_test`) gates.

## Run

```bash
pip install -r requirements.txt
python -m src.main -p 0.1
python -m pytest
```

```
$ python -m src.main
error on   syndrome   corrected   fidelity
none       00         -           1.0000
q0         01         q0          1.0000
q1         11         q1          1.0000
q2         10         q2          1.0000
q0,q1      10         q2          0.0127

flip probability p = 0.1
logical error rate   0.0290  (theory 0.0280, bare qubit 0.1)
```

## How it works

| Syndrome (q4 q3) | Meaning |
| --- | --- |
| 00 | no error |
| 01 | q0 flipped |
| 11 | q1 flipped |
| 10 | q2 flipped |

q3 holds q0 ⊕ q1 and q4 holds q1 ⊕ q2. After the correction the circuit decodes, and the check compares q0 with the input state by fidelity.

Two flips look like one flip on the remaining qubit, so the decoder makes things worse and the logical qubit ends up flipped (last row above). `logical_error_rate` applies a random X to each data qubit with probability p using an Aer noise instruction and compares the result with 3p² − 2p³.

This code only handles bit flips. A phase flip (Z error) passes straight through it; protecting against both needs a larger code such as Shor's nine-qubit code.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.
