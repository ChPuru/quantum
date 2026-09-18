import argparse

from src.bb84 import QBER_LIMIT, run


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate BB84 key distribution.")
    parser.add_argument("--bits", type=int, default=64, help="qubits Alice sends")
    parser.add_argument("--eavesdrop", action="store_true", help="add an intercept-resend Eve")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    r = run(args.bits, eavesdrop=args.eavesdrop, seed=args.seed)
    print(f"sent                {args.bits} qubits")
    print(f"same basis          {len(r.sifted)}")
    print(f"revealed for check  {len(r.checked)}")
    print(f"QBER                {r.qber:.1%} (abort above {QBER_LIMIT:.0%})")
    if r.aborted:
        print("result              aborted, the channel looks tapped")
    else:
        print(f"{f'key ({len(r.alice_key)} bits)':<20}{r.alice_key}")
        print(f"keys match          {r.alice_key == r.bob_key}")


if __name__ == "__main__":
    main()
