"""Qubit Hamiltonian for H2 in the STO-3G basis, computed from scratch.

Each hydrogen gets one 1s orbital made of three Gaussians. The Gaussian
integrals have closed forms (Szabo and Ostlund, Modern Quantum Chemistry,
appendix A), so no chemistry package is needed. By symmetry the two
molecular orbitals are sigma_g = (1s_A + 1s_B) and sigma_u = (1s_A - 1s_B),
normalised, which is also the restricted Hartree-Fock solution.

Four spin orbitals map to four qubits with the Jordan-Wigner transform:

    qubit 0: sigma_g up     qubit 1: sigma_g down
    qubit 2: sigma_u up     qubit 3: sigma_u down

The Hartree-Fock state fills qubits 0 and 1, which is |0011>.
Energies are in hartree. Bond lengths are in angstrom.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np
from qiskit.quantum_info import SparsePauliOp
from scipy.special import erf

ANGSTROM_TO_BOHR = 1.0 / 0.529177210903

# STO-3G hydrogen 1s: exponents (bohr^-2) and contraction coefficients.
STO3G_EXPONENTS = np.array([3.42525091, 0.62391373, 0.16885540])
STO3G_COEFFS = np.array([0.15432897, 0.53532814, 0.44463454])


@dataclass(frozen=True)
class H2Hamiltonian:
    bond_length: float  # angstrom
    qubit_op: SparsePauliOp  # includes nuclear repulsion as an identity term
    nuclear_repulsion: float
    hf_energy: float
    fci_energy: float  # exact ground state in the two-electron sector


def _boys0(t: float) -> float:
    if t < 1e-8:
        return 1.0 - t / 3.0
    return 0.5 * math.sqrt(math.pi / t) * erf(math.sqrt(t))


def _norm(a: float) -> float:
    return (2 * a / math.pi) ** 0.75


def _atomic_integrals(r_bohr: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Overlap S, core Hamiltonian h = T + V, and two-electron integrals (pq|rs) over 1s_A, 1s_B."""
    centres = [np.zeros(3), np.array([0.0, 0.0, r_bohr])]
    exps = STO3G_EXPONENTS
    coefs = STO3G_COEFFS * np.array([_norm(a) for a in exps])  # fold in primitive normalisation

    s = np.zeros((2, 2))
    h = np.zeros((2, 2))
    eri = np.zeros((2, 2, 2, 2))

    for mu, nu in itertools.product(range(2), repeat=2):
        a_pos, b_pos = centres[mu], centres[nu]
        rab2 = float(np.sum((a_pos - b_pos) ** 2))
        for (a, ca), (b, cb) in itertools.product(zip(exps, coefs, strict=True), repeat=2):
            p = a + b
            k = math.exp(-a * b / p * rab2)
            overlap = (math.pi / p) ** 1.5 * k
            s[mu, nu] += ca * cb * overlap
            h[mu, nu] += ca * cb * a * b / p * (3 - 2 * a * b / p * rab2) * overlap
            centre_p = (a * a_pos + b * b_pos) / p
            for nucleus in centres:
                rpc2 = float(np.sum((centre_p - nucleus) ** 2))
                h[mu, nu] -= ca * cb * 2 * math.pi / p * k * _boys0(p * rpc2)

    for mu, nu, lam, sig in itertools.product(range(2), repeat=4):
        pa, pb, pc, pd = (centres[i] for i in (mu, nu, lam, sig))
        rab2 = float(np.sum((pa - pb) ** 2))
        rcd2 = float(np.sum((pc - pd) ** 2))
        total = 0.0
        for (a, ca), (b, cb), (c, cc), (d, cd) in itertools.product(
            zip(exps, coefs, strict=True), repeat=4
        ):
            p, q = a + b, c + d
            centre_p = (a * pa + b * pb) / p
            centre_q = (c * pc + d * pd) / q
            rpq2 = float(np.sum((centre_p - centre_q) ** 2))
            total += (
                ca
                * cb
                * cc
                * cd
                * 2
                * math.pi**2.5
                / (p * q * math.sqrt(p + q))
                * math.exp(-a * b / p * rab2 - c * d / q * rcd2)
                * _boys0(p * q / (p + q) * rpq2)
            )
        eri[mu, nu, lam, sig] = total
    return s, h, eri


def _ladder(p: int, n: int, create: bool) -> SparsePauliOp:
    """Jordan-Wigner a_p^dagger (create=True) or a_p on n qubits."""
    sign = -1j if create else 1j
    z_string = SparsePauliOp.from_sparse_list([("Z" * p, list(range(p)), 1.0)], n)
    local = SparsePauliOp.from_sparse_list([("X", [p], 0.5), ("Y", [p], 0.5 * sign)], n)
    return local @ z_string


def h2_hamiltonian(bond_length: float) -> H2Hamiltonian:
    if bond_length <= 0:
        raise ValueError("bond length must be positive")
    r = bond_length * ANGSTROM_TO_BOHR
    s, h_ao, eri_ao = _atomic_integrals(r)

    c = np.array(
        [
            [1, 1] / np.sqrt(2 * (1 + s[0, 1])),  # sigma_g
            [1, -1] / np.sqrt(2 * (1 - s[0, 1])),  # sigma_u
        ]
    ).T
    h_mo = c.T @ h_ao @ c
    eri_mo = np.einsum("ap,bq,cr,ds,abcd->pqrs", c, c, c, c, eri_ao)

    # Spin orbital k = 2 * spatial + spin.
    n = 4
    ops: list[SparsePauliOp] = []
    create = [_ladder(k, n, True) for k in range(n)]
    annihilate = [_ladder(k, n, False) for k in range(n)]

    for p, q in itertools.product(range(n), repeat=2):
        if p % 2 == q % 2 and abs(h_mo[p // 2, q // 2]) > 1e-12:
            ops.append(h_mo[p // 2, q // 2] * (create[p] @ annihilate[q]))

    # 1/2 sum (pr|qs) a_p^+ a_q^+ a_s a_r, chemist notation, spin conserved per electron.
    for p, q, r_, s_ in itertools.product(range(n), repeat=4):
        if p % 2 != r_ % 2 or q % 2 != s_ % 2:
            continue
        g = eri_mo[p // 2, r_ // 2, q // 2, s_ // 2]
        if abs(g) < 1e-12:
            continue
        term = create[p] @ create[q] @ annihilate[s_] @ annihilate[r_]
        ops.append(0.5 * g * term)

    nuclear = 1.0 / r
    op = sum(ops, SparsePauliOp("I" * n, nuclear)).simplify(atol=1e-12)
    op = SparsePauliOp(op.paulis, op.coeffs.real)  # Hermitian, so imaginary parts are round-off

    matrix = op.to_matrix()
    two_electron = [i for i in range(2**n) if bin(i).count("1") == 2]
    block = matrix[np.ix_(two_electron, two_electron)]
    hf_index = 0b0011

    return H2Hamiltonian(
        bond_length=bond_length,
        qubit_op=op,
        nuclear_repulsion=nuclear,
        hf_energy=float(matrix[hf_index, hf_index].real),
        fci_energy=float(np.linalg.eigvalsh(block)[0]),
    )
