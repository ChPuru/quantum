import argparse

from src.qnn_classifier import QNNClassifier, make_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a VQC on two Gaussian blobs.")
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--maxiter", type=int, default=60)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    data = make_dataset(args.samples, seed=args.seed)
    print(f"{len(data.x_train)} training samples, {len(data.x_test)} test samples")

    model = QNNClassifier(maxiter=args.maxiter, seed=args.seed).fit(data.x_train, data.y_train)
    print(f"final training loss  {model.loss_history[-1]:.4f}")
    print(f"train accuracy       {model.score(data.x_train, data.y_train):.1%}")
    print(f"test accuracy        {model.score(data.x_test, data.y_test):.1%}")


if __name__ == "__main__":
    main()
