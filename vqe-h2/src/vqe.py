"""VQE for H2 with a one-parameter ansatz.

Particle number, spin and the molecule's inversion symmetry leave only two
determinants in the H2 ground state: both electrons in sigma_g (|0011>, the
Hartree-Fock state) or both in sigma_u (|1100>). One angle covers that space:

    |psi(theta)> = cos(theta/2) |0011> + sin(theta/2) |1100>

so VQE with this ansatz can reach the exact (full CI) energy. A generic
hardware-efficient ansatz would need more parameters and more luck.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator
from scipy.optimize import minimize

from src.h2_hamiltonian import h2_hamiltonian


@dataclass(frozen=True)
class VQEResult:
    bond_length: float
    energy: float
    theta: float
    evaluations: int
    hf_energy: float
    fci_energy: float


def ansatz() -> QuantumCircuit:
    theta = Parameter("theta")
    qc = QuantumCircuit(4)
    qc.ry(theta, 2)
    qc.cx(2, 3)  # cos|00> + sin|11> on the sigma_u pair
    qc.x(2)
    qc.cx(2, 0)  # when sigma_u is empty, fill sigma_g
    qc.cx(2, 1)
    qc.x(2)
    return qc


def run_vqe(bond_length: float) -> VQEResult:
    """Minimise <H> from the Hartree-Fock point theta = 0 with COBYLA."""
    h2 = h2_hamiltonian(bond_length)
    circuit = ansatz()
    estimator = StatevectorEstimator()
    evaluations = 0

    def energy(params: np.ndarray) -> float:
        nonlocal evaluations
        evaluations += 1
        result = estimator.run([(circuit, h2.qubit_op, params)]).result()
        return float(result[0].data.evs)

    res = minimize(energy, x0=[0.0], method="COBYLA", options={"rhobeg": 0.5, "tol": 1e-8})
    return VQEResult(
        bond_length=bond_length,
        energy=float(res.fun),
        theta=float(res.x[0]),
        evaluations=evaluations,
        hf_energy=h2.hf_energy,
        fci_energy=h2.fci_energy,
    )


def dissociation_curve(bond_lengths: list[float]) -> list[VQEResult]:
    return [run_vqe(r) for r in bond_lengths]
