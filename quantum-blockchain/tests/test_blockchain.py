import itertools

import pytest

from src.blockchain import Block, Blockchain
from src.quantum_validator import QuantumValidator


@pytest.fixture
def chain() -> Blockchain:
    bc = Blockchain(QuantumValidator(num_qubits=4))
    for i, data in enumerate(["a", "b", "c"]):
        bc.mine(data, timestamp=float(i + 1))
    return bc


def test_mined_chain_is_valid(chain: Blockchain) -> None:
    assert len(chain.chain) == 4
    assert chain.is_valid()
    for block in chain.chain[1:]:
        assert chain.validator.is_valid(block.compute_hash())


def test_blocks_link_to_parents(chain: Blockchain) -> None:
    for parent, block in itertools.pairwise(chain.chain):
        assert block.previous_hash == parent.compute_hash()
        assert block.index == parent.index + 1


def test_editing_a_block_breaks_the_chain(chain: Blockchain) -> None:
    chain.chain[1].data = "tampered"
    assert not chain.is_valid()


def test_editing_the_last_block_fails_validation(chain: Blockchain) -> None:
    chain.chain[-1].data = "tampered"
    assert not chain.is_valid()


def test_validation_is_deterministic() -> None:
    validator = QuantumValidator(num_qubits=4)
    block_hash = Block(1, "x", "0" * 64, timestamp=0.0).compute_hash()
    assert len({validator.is_valid(block_hash) for _ in range(20)}) == 1


def test_probabilities_sum_to_one() -> None:
    probs = QuantumValidator(3).probabilities("0123456789abcdef" * 4)
    assert sum(probs.values()) == pytest.approx(1.0)


def test_hash_depends_on_every_field() -> None:
    base = Block(1, "x", "0" * 64, timestamp=1.0, nonce=0)
    changed = [
        Block(2, "x", "0" * 64, timestamp=1.0, nonce=0),
        Block(1, "y", "0" * 64, timestamp=1.0, nonce=0),
        Block(1, "x", "1" * 64, timestamp=1.0, nonce=0),
        Block(1, "x", "0" * 64, timestamp=2.0, nonce=0),
        Block(1, "x", "0" * 64, timestamp=1.0, nonce=1),
    ]
    assert len({base.compute_hash(), *(b.compute_hash() for b in changed)}) == 6


def test_mining_gives_up_after_max_nonce() -> None:
    bc = Blockchain(QuantumValidator(num_qubits=6), max_nonce=3)
    with pytest.raises(RuntimeError):
        bc.mine("hard", timestamp=0.0)


@pytest.mark.parametrize(("n", "target"), [(4, "111"), (3, "10a"), (0, "")])
def test_rejects_bad_targets(n: int, target: str) -> None:
    with pytest.raises(ValueError):
        QuantumValidator(n, target)
