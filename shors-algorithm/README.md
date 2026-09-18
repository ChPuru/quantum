# Shor's algorithm

Factors small integers with Shor's algorithm on the Qiskit Aer simulator. The quantum part is order finding with quantum phase estimation. Everything else is classical.

## Run

```bash
pip install -r requirements.txt
python -m src.main 15 -a 7        # force a = 7
python -m src.main 35 --seed 1    # random a
python -m pytest
```

```
$ python -m src.main 21 -a 2 --seed 1
21 = 7 x 3  (method: order finding)
a = 2, order r = 6, attempts = 1
```

## How it works

1. Handle the classical cases first: even N, and N = b^k.
2. Pick a random a. If gcd(a, N) > 1, that gcd is already a factor.
3. Otherwise run order finding. For an n-bit N the circuit has 2n counting qubits and n work qubits. Counting qubit j controls multiplication by a^(2^j) mod N, followed by an inverse QFT and a measurement.
4. Continued fractions turn each reading y into a fraction close to y / 2^(2n). Its denominator is r or a divisor of r, so the code also tries the lcm of the denominators and keeps the first candidate with a^r = 1 (mod N).
5. If r is even and a^(r/2) is not -1 (mod N), then gcd(a^(r/2) - 1, N) or gcd(a^(r/2) + 1, N) is a factor. If not, try another a.

## Limits

Modular multiplication is built as a permutation matrix (`UnitaryGate`) instead of a gate-level arithmetic circuit. It is exact for any N, but the matrix doubles in size with each extra bit, so `factor` refuses N with more than 7 bits (N >= 128). A 7-bit N uses 21 qubits and takes about 15 seconds per attempt.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.

## Credits

The phase-estimation layout follows the Shor's algorithm chapter of the [Qiskit Textbook](https://github.com/Qiskit/textbook) (Apache-2.0). See NOTICE in the repository root.
