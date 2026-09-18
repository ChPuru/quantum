# VQE for the H2 molecule

Computes the ground-state energy of H2 across bond lengths with the variational quantum eigensolver and compares it with Hartree-Fock and the exact (full CI) result.

## Run

```bash
pip install -r requirements.txt
python -m src.main --start 0.3 --stop 2.5 --points 12
python -m pytest
```

```
$ python -m src.main --points 6
 R (A)    HF (Ha)      VQE (Ha)     exact (Ha)   VQE error
 0.30    -0.593828    -0.601804    -0.601804  2.2e-16
 0.74    -1.116759    -1.137284    -1.137284  4.4e-16
 1.18    -1.011474    -1.061197    -1.061197  2.2e-16
 1.62    -0.876107    -0.980857    -0.980857  1.1e-16
 2.06    -0.771797    -0.945931    -0.945931  3.3e-16
 2.50    -0.702944    -0.936055    -0.936055  3.3e-16

lowest VQE energy -1.137284 Ha at R = 0.74 A
```

The notebook plots the full dissociation curve.

## How it works

**Hamiltonian** (`src/h2_hamiltonian.py`). The code computes STO-3G integrals from their closed-form Gaussian expressions (Szabo and Ostlund, *Modern Quantum Chemistry*, appendix A), so there is no chemistry dependency and it runs on Windows. Symmetry fixes the two molecular orbitals, σg and σu. The four spin orbitals map to four qubits with the Jordan-Wigner transform, which gives a 15-term Pauli operator. Hartree-Fock and full-CI energies match PySCF to about 1e-8 hartree; the tests pin reference values.

**Ansatz** (`src/vqe.py`). Spin, particle number and inversion symmetry leave only two determinants in the ground state: |0011⟩ (Hartree-Fock) and |1100⟩ (both electrons in σu). One RY angle plus a few CNOTs spans that pair, so VQE can reach the exact energy. That is a property of this tiny molecule, not of VQE in general. Larger molecules need many-parameter ansätze and run into optimisation and noise problems this example does not show.

**Optimiser.** COBYLA from the Hartree-Fock point, with Qiskit's exact `StatevectorEstimator`, so there is no shot noise.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2.
