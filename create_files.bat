@echo off
REM Create root .gitignore
(
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.pyd
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo MANIFEST
) > .gitignore
REM Create root README.md
(
echo # Quantum Computing Workspace
echo.
echo This repository contains implementations of various quantum computing algorithms and applications.
echo.
echo ## Projects
echo.
echo - **grover-search**: Implementation of Grover's search algorithm
echo - **qaoa-maxcut**: Quantum Approximate Optimization Algorithm for the MaxCut problem
echo - **qec-bitflip**: Quantum Error Correction using the Bit Flip Code
echo - **qkd-bb84**: Quantum Key Distribution using the BB84 protocol
echo - **qrng**: Quantum Random Number Generator
echo - **quantum-annealing**: Quantum Annealing simulation
echo - **quantum-blockchain**: Quantum-enhanced blockchain validation
echo - **quantum-game-theory**: Quantum game theory demonstration with penny flip game
echo - **quantum-ml-qnn**: Quantum Neural Network for image classification
echo - **quantum-secure-storage**: Quantum secure storage system
echo - **quantum-teleportation**: Quantum teleportation protocol
echo - **shors-algorithm**: Shor's factoring algorithm
echo - **vqe-h2**: Variational Quantum Eigensolver for H2 molecule energy calculation
) > README.md
REM List of projects
set projects=grover-search qaoa-maxcut qec-bitflip qkd-bb84 qrng quantum-annealing quantum-blockchain quantum-game-theory quantum-ml-qnn quantum-secure-storage quantum-teleportation shors-algorithm vqe-h2
for %%p in (%projects%) do (
  copy .gitignore %%p\.gitignore
  REM Create README for %%p
  if "%%p"=="grover-search" (
    (
    echo # Grover Search
    echo.
    echo This project implements Grover's quantum search algorithm.
    ) > %%p\README.md
  )
  if "%%p"=="qaoa-maxcut" (
    (
    echo # QAOA MaxCut
    echo.
    echo This project implements the Quantum Approximate Optimization Algorithm for the MaxCut problem.
    ) > %%p\README.md
  )
  if "%%p"=="qec-bitflip" (
    (
    echo # Quantum Error Correction - Bit Flip Code
    echo.
    echo This project demonstrates quantum error correction using the bit flip code.
    ) > %%p\README.md
  )
  if "%%p"=="qkd-bb84" (
    (
    echo # BB84 Quantum Key Distribution
    echo.
    echo This project implements the BB84 protocol for quantum key distribution.
    ) > %%p\README.md
  )
  if "%%p"=="qrng" (
    (
    echo # Quantum Random Number Generator
    echo.
    echo This project provides a quantum random number generator implementation.
    ) > %%p\README.md
  )
  if "%%p"=="quantum-annealing" (
    (
    echo # Quantum Annealing
    echo.
    echo This project simulates quantum annealing processes.
    ) > %%p\README.md
  )
  if "%%p"=="quantum-blockchain" (
    (
    echo # Quantum Blockchain
    echo.
    echo This project explores quantum-enhanced blockchain validation.
    ) > %%p\README.md
  )
  if "%%p"=="quantum-game-theory" (
    (
    echo # Quantum Game Theory
    echo.
    echo This project demonstrates quantum game theory with a penny flip game.
    ) > %%p\README.md
  )
  if "%%p"=="quantum-ml-qnn" (
    (
    echo # Quantum Neural Network Classifier
    echo.
    echo This project implements a quantum neural network for image classification.
    ) > %%p\README.md
  )
  if "%%p"=="quantum-secure-storage" (
    (
    echo # Quantum Secure Storage
    echo.
    echo This project provides a quantum secure storage system.
    ) > %%p\README.md
  )
  if "%%p"=="quantum-teleportation" (
    (
    echo # Quantum Teleportation
    echo.
    echo This project implements the quantum teleportation protocol.
    ) > %%p\README.md
  )
  if "%%p"=="shors-algorithm" (
    (
    echo # Shor's Algorithm
    echo.
    echo This project implements Shor's quantum factoring algorithm.
    ) > %%p\README.md
  )
  if "%%p"=="vqe-h2" (
    (
    echo # VQE for H2 Molecule
    echo.
    echo This project uses Variational Quantum Eigensolver to calculate H2 molecule energy.
    ) > %%p\README.md
  )
)