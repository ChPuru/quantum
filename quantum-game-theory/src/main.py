# src/main.py

from src.quantum_penny_flip import QuantumPennyFlip

def main():
    NUM_GAMES = 1000
    game_simulator = QuantumPennyFlip()

    print("--- Quantum Penny Flip Game Simulation ---")

    # --- Scenario 1: Classical vs. Classical ---
    # Q's classical strategy is to do nothing ('identity').
    # Picard randomly flips or does nothing.
    print(f"\nRunning {NUM_GAMES} games with Classical strategies...")
    classical_win_rate = game_simulator.simulate_games(
        num_games=NUM_GAMES,
        q_strategy='identity',
        picard_strategy='random' # This is handled inside the simulate_games loop
    )
    print(f"Q's Win Rate (Classical Strategy): {classical_win_rate:.2%}")

    # --- Scenario 2: Quantum vs. Classical ---
    # Q's quantum strategy is to apply a Hadamard gate.
    # Picard randomly flips or does nothing.
    print(f"\nRunning {NUM_GAMES} games with Q's Quantum strategy...")
    quantum_win_rate = game_simulator.simulate_games(
        num_games=NUM_GAMES,
        q_strategy='hadamard',
        picard_strategy='random'
    )
    print(f"Q's Win Rate (Quantum Strategy): {quantum_win_rate:.2%}")

    print("\n--- Conclusion ---")
    if quantum_win_rate > classical_win_rate + 0.4:
        print("The quantum strategy provides a decisive advantage, as expected.")
    else:
        print("The quantum strategy did not show a significant advantage.")
    print("------------------")

if __name__ == "__main__":
    main()