# Meyer's quantum penny flip

A coin starts heads up. Q moves, Picard moves, Q moves again, and Q wins if the coin shows heads. Picard may only flip the coin or leave it. The game comes from D. A. Meyer, *Quantum Strategies*, Phys. Rev. Lett. 82, 1052 (1999).

## Run

```bash
pip install -r requirements.txt
python -m src.main --games 10000
python -m pytest
```

```
$ python -m src.main
P(Q wins) for each pure Q strategy
Q moves   Picard I   Picard X
I, I      1.00       0.00
I, X      0.00       1.00
I, H      0.50       0.50
X, I      0.00       1.00
X, X      1.00       0.00
X, H      0.50       0.50
H, I      0.50       0.50
H, X      0.50       0.50
H, H      1.00       1.00

10000 games against a Picard who flips at random
classical Q wins    50.3%
quantum Q wins      100.0%
```

## Why H, H wins

Q's first H turns |0⟩ into |+⟩. Picard's X maps |+⟩ to itself, so flipping and not flipping look the same. Q's second H turns |+⟩ back into |0⟩: heads, every time. Every classical Q strategy wins half the time against a Picard who flips at random.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.
