# QAOA for MaxCut

Splits the nodes of a graph into two groups so that as many edges (or as much edge weight) as possible cross between them, using the Quantum Approximate Optimization Algorithm.

## Run

```bash
pip install -r requirements.txt
python -m src.main --reps 2
python -m pytest
```

```
$ python -m src.main
edges               [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
partition           [1, 3] | [0, 2]
cut value           4 (brute force: 4)
expected cut <C>    3.742
P(best cut)         84.9%
```

## How it works

1. Cost operator H = Σ w_ij Z_i Z_j. Its lowest-energy basis states are the maximum cuts.
2. Circuit: Hadamards on every qubit, then p layers of RZZ(2γw) on each edge and RX(2β) on each node.
3. SciPy's COBYLA minimises ⟨H⟩ over the 2p angles, from 5 random starts because the landscape has local minima.
4. The optimised circuit is sampled, and the best cut among the samples is returned together with the share of shots that hit a maximum cut.

Everything runs on Qiskit's exact statevector primitives, so there is no shot noise in the optimisation. `brute_force_maxcut` checks results on small graphs. Nodes can have any hashable labels, and edges can carry a `weight` attribute.

Tested with Python 3.12 on Qiskit 2.1.1 with Aer 0.17.0, and on Qiskit 2.5.2 with Aer 0.17.2. The simulator packages are not needed here.
