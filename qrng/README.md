# Qubit random number generator

Produces random bits by measuring a qubit in the |+⟩ state, and uses them for unbiased random integers.

## Run

```bash
pip install -r requirements.txt
python -m src.main --bits 16 --dice --seed 3
python -m pytest
```

```
$ python -m src.main --bits 16 --dice --seed 3
     ┌───┐┌─┐
  q: ┤ H ├┤M├
     └───┘└╥┘
c: 1/══════╩═
           0
bits    0011100101010101
die     5
```

## Notes

- One qubit, many shots: each shot is one bit.
- `random_int(low, high)` draws just enough bits for the range and throws away values past the top (rejection sampling). Reducing mod the range size would favour small values.
- **These bits are not quantum random.** On the Aer simulator they come from Aer's pseudorandom generator and repeat for the same seed. On real hardware the same circuit gives measurement randomness, with some device bias that a real QRNG would remove with a randomness extractor. Use Python's `secrets` module for anything security-related.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.
