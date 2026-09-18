import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from src.h2_hamiltonian import h2_hamiltonian
from src.vqe import ansatz, run_vqe

# Reference energies (hartree) from PySCF 2.14, RHF and FCI with basis="sto-3g".
REFERENCE = {
    0.3: (-0.59382776, -0.60180371),
    0.7414: (-1.11668439, -1.13727017),
    1.5: (-0.91087355, -0.99814935),
    4.0: (-0.61486997, -0.93317136),
}


@pytest.mark.parametrize(("r", "energies"), REFERENCE.items())
def test_hamiltonian_matches_pyscf(r: float, energies: tuple[float, float]) -> None:
    h2 = h2_hamiltonian(r)
    assert h2.hf_energy == pytest.approx(energies[0], abs=1e-6)
    assert h2.fci_energy == pytest.approx(energies[1], abs=1e-6)


def test_hamiltonian_shape() -> None:
    op = h2_hamiltonian(0.74).qubit_op
    assert op.num_qubits == 4
    assert len(op) == 15
    assert np.allclose(op.coeffs.imag, 0)
    assert np.allclose(op.to_matrix(), op.to_matrix().conj().T)


def test_separated_atoms() -> None:
    # Far apart, the exact energy approaches two STO-3G hydrogen atoms (2 x -0.46658 Ha)
    # while Hartree-Fock stays too high: the textbook failure of a single determinant.
    h2 = h2_hamiltonian(6.0)
    assert h2.fci_energy == pytest.approx(2 * -0.466582, abs=1e-4)
    assert h2.hf_energy > h2.fci_energy + 0.2


def test_ansatz_starts_at_hartree_fock() -> None:
    state = Statevector(ansatz().assign_parameters([0.0]))
    assert state.equiv(Statevector.from_label("0011"))


def test_ansatz_reaches_doubly_excited_state() -> None:
    state = Statevector(ansatz().assign_parameters([np.pi]))
    assert state.equiv(Statevector.from_label("1100"))


@pytest.mark.parametrize("r", [0.5, 0.7414, 1.2, 2.0, 3.0])
def test_vqe_reaches_exact_energy(r: float) -> None:
    result = run_vqe(r)
    assert result.energy == pytest.approx(result.fci_energy, abs=1e-6)
    assert result.energy < result.hf_energy


def test_equilibrium_bond_length() -> None:
    grid = np.arange(0.60, 0.90, 0.01)
    energies = [h2_hamiltonian(r).fci_energy for r in grid]
    assert grid[int(np.argmin(energies))] == pytest.approx(0.735, abs=0.011)


def test_rejects_non_positive_bond_length() -> None:
    with pytest.raises(ValueError):
        h2_hamiltonian(0.0)
