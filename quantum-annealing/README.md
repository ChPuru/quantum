# Simulated quantum annealing for MaxCut

Simulates adiabatic quantum annealing on a MaxCut problem by integrating the Schrödinger equation exactly, and shows how the anneal time controls the chance of ending on a maximum cut.

## Run

```bash
pip install -r requirements.txt
python -m src.main --time 10
python -m pytest
```

```
$ python -m src.main
most likely cut     [2, 4] | [0, 1, 3]
cut value           6 (maximum 6)
P(maximum cut)      97.4%

anneal time vs P(maximum cut)
  T = 0.5  8.8%
  T = 2    37.4%
  T = 5    86.3%
  T = 10   97.4%
  T = 20   99.9%
```

## How it works

H(s) = (1 − s)·H_driver + s·H_problem, with s swept linearly from 0 to 1 over time T:

- H_driver = −Σ X_i. Its ground state |+⟩^n is where the anneal starts.
- H_problem = Σ w_ij Z_i Z_j. Its ground states are the maximum cuts.

The state is advanced in small slices with `scipy.sparse.linalg.expm_multiply`. If T is long compared with the inverse of the smallest energy gap, the state tracks the ground state and ends on a maximum cut (adiabatic theorem).

## Limits

This is a classical simulation. Qiskit only builds the Pauli operators, nothing runs on an annealer, and the statevector limits it to 16 nodes. Real annealers also contend with noise, temperature and limited qubit connectivity, none of which appear here.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.
