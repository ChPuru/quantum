import numpy as np
import pytest

from src.bb84 import X, Z, bb84_circuit, run


def test_no_eavesdropper_gives_matching_keys() -> None:
    for seed in range(5):
        r = run(200, seed=seed)
        assert r.qber == 0.0
        assert not r.aborted
        assert r.alice_key == r.bob_key
        assert len(r.alice_key) == len(r.sifted) - len(r.checked)


def test_bob_reads_alice_whenever_bases_match() -> None:
    r = run(500, seed=1)
    np.testing.assert_array_equal(r.alice_bits[r.sifted], r.bob_bits[r.sifted])


def test_mismatched_bases_give_coin_flips() -> None:
    r = run(4000, seed=2)
    other = np.flatnonzero(r.alice_bases != r.bob_bases)
    agreement = np.mean(r.alice_bits[other] == r.bob_bits[other])
    assert agreement == pytest.approx(0.5, abs=0.04)


def test_eavesdropper_causes_quarter_error_rate() -> None:
    r = run(4000, eavesdrop=True, seed=3)
    assert r.qber == pytest.approx(0.25, abs=0.03)
    assert r.aborted


def test_sifting_and_sampling_sizes() -> None:
    r = run(1000, seed=4)
    assert len(r.sifted) == pytest.approx(500, abs=60)
    assert len(r.checked) == round(len(r.sifted) * 0.5)
    assert set(r.checked) <= set(r.sifted)


def test_fixed_inputs() -> None:
    bits = np.array([0, 1, 1, 0])
    bases = np.array([Z, Z, X, X])
    qc = bb84_circuit(bits, bases, bases)
    assert qc.count_ops()["h"] == 4  # two for Alice, two for Bob
    assert qc.count_ops()["x"] == 2


def test_same_seed_same_run() -> None:
    assert run(100, eavesdrop=True, seed=7).alice_key == run(100, eavesdrop=True, seed=7).alice_key


@pytest.mark.parametrize(("n", "fraction"), [(0, 0.5), (10, 0.0), (10, 1.0)])
def test_rejects_bad_input(n: int, fraction: float) -> None:
    with pytest.raises(ValueError):
        run(n, check_fraction=fraction)
