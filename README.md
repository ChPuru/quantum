# Quantum computing workspace

Small Qiskit projects, one per folder. Each has its own README, `requirements.txt`, `src/`, `tests/` and a notebook.

- **grover-search**: Grover search for one or more marked bitstrings
- **qaoa-maxcut**: QAOA for weighted MaxCut, checked against brute force
- **qec-bitflip**: three-qubit bit-flip code with feed-forward correction
- **qkd-bb84**: BB84 key distribution with an intercept-resend eavesdropper
- **qrng**: random bits and unbiased integers from measuring |+>
- **quantum-annealing**: exact simulation of adiabatic annealing for MaxCut
- **quantum-blockchain**: toy chain with a circuit-based proof of work
- **quantum-game-theory**: Meyer's quantum penny flip game
- **quantum-ml-qnn**: variational quantum classifier on 2-D synthetic data
- **quantum-secure-storage**: simulated BB84 key feeding AES-256-GCM encryption
- **quantum-teleportation**: one-qubit teleportation with dynamic circuits
- **shors-algorithm**: Shor's factoring algorithm for small N
- **vqe-h2**: VQE dissociation curve of H2, with the Hamiltonian built from scratch

Run each project from its own folder, for example:

```bash
cd shors-algorithm
pip install -r requirements.txt
python -m src.main
python -m pytest
```

Everything runs on simulators. Some projects are demos of an idea rather than useful tools (the blockchain and secure-storage projects in particular); their READMEs say where the limits are.

## License

MIT, see [LICENSE](LICENSE). Some files adapt code from the Qiskit Textbook, which is Apache-2.0; [NOTICE](NOTICE) lists them.
