from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).parent
RESULTS_PATH = BASE_DIR / "results" / "sample_backtest_results.csv"
CHART_PATH = BASE_DIR / "assets" / "equity_curve.png"


def main() -> None:
    results = pd.read_csv(RESULTS_PATH)
    if results.empty:
        raise ValueError("Backtest results are empty. Run run_analysis.py first.")

    CHART_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(results["trade"], results["balance"], marker="o", linewidth=2)
    ax.axhline(results["balance"].iloc[0] - results["pnl"].iloc[0], linestyle="--", linewidth=1)
    ax.set_title("Backtest Equity Curve")
    ax.set_xlabel("Trade Number")
    ax.set_ylabel("Account Balance ($)")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(CHART_PATH, dpi=160)

    print(f"Equity curve saved to {CHART_PATH}")


if __name__ == "__main__":
    main()
