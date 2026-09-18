# Grover search

Finds one or more marked bitstrings among 2^n with Grover's algorithm on the Qiskit Aer simulator.

## Run

```bash
pip install -r requirements.txt
python -m src.main 101 --seed 1
python -m src.main 0110 1001      # two marked strings
python -m pytest
```

```
$ python -m src.main 101 --seed 1
iterations          2
most frequent       101
hit rate            94.9%
theoretical         94.5%
```

## How it works

- The oracle flips the sign of each marked state: X gates on the qubits that should be 0, a multi-controlled Z, then the X gates again.
- The diffuser reflects about the uniform superposition.
- With M marked strings out of N = 2^n, each round rotates the state by 2θ, where sin θ = √(M/N). The code runs floor(π / 4θ) rounds, and the success probability after k rounds is sin²((2k + 1)θ). The notebook shows what happens when you stop too early or run too long.

Bitstrings follow Qiskit's ordering, with the leftmost character on the highest qubit. The string you mark is the string you see in the counts.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.

## Credits

The diffuser follows the Grover's algorithm chapter of the [Qiskit Textbook](https://github.com/Qiskit/textbook) (Apache-2.0). See NOTICE in the repository root.
