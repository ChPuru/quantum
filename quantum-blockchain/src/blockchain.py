"""A minimal hash-linked chain whose proof of work is QuantumValidator."""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from dataclasses import asdict, dataclass, field

from src.quantum_validator import QuantumValidator


@dataclass
class Block:
    index: int
    data: str
    previous_hash: str
    timestamp: float = field(default_factory=time.time)
    nonce: int = 0

    def compute_hash(self) -> str:
        # JSON with sorted keys, so ("1", "23") and ("12", "3") can't collide
        # the way plain string concatenation can.
        payload = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()


class Blockchain:
    def __init__(self, validator: QuantumValidator, max_nonce: int = 100_000) -> None:
        self.validator = validator
        self.max_nonce = max_nonce
        self.chain = [Block(0, "genesis", "0" * 64, timestamp=0.0)]

    @property
    def latest(self) -> Block:
        return self.chain[-1]

    def mine(self, data: str, timestamp: float | None = None) -> Block:
        """Try nonces until the block's circuit favours the target, then append it."""
        block = Block(
            index=self.latest.index + 1,
            data=data,
            previous_hash=self.latest.compute_hash(),
            timestamp=time.time() if timestamp is None else timestamp,
        )
        for nonce in range(self.max_nonce):
            block.nonce = nonce
            if self.validator.is_valid(block.compute_hash()):
                self.chain.append(block)
                return block
        raise RuntimeError(f"no valid nonce below {self.max_nonce}")

    def is_valid(self) -> bool:
        """Every block links to its parent and passes the validator (genesis excepted)."""
        for parent, block in itertools.pairwise(self.chain):
            if block.previous_hash != parent.compute_hash():
                return False
            if not self.validator.is_valid(block.compute_hash()):
                return False
        return True
