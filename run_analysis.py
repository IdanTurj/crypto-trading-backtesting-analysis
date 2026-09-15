from pathlib import Path

import pandas as pd

from src.backtest import BacktestConfig, run_backtest


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "sample_prices.csv"
RESULTS_PATH = BASE_DIR / "results" / "sample_backtest_results.csv"


def format_summary(summary: dict) -> list[str]:
    return [
        f"Total trades: {summary['total_trades']}",
        f"Winning trades: {summary['winning_trades']}",
        f"Losing trades: {summary['losing_trades']}",
        f"Win rate: {summary['win_rate']:.2f}%",
        f"Net P&L: ${summary['net_pnl']:.2f}",
        f"Return: {summary['return_pct']:.2f}%",
        f"Profit factor: {summary['profit_factor']:.2f}",
        f"Final balance: ${summary['final_balance']:.2f}",
        f"Maximum drawdown: ${summary['max_drawdown']:.2f}",
        f"Maximum drawdown: {summary['max_drawdown_pct']:.2f}%",
        f"Maximum wager: ${summary['max_wager']:.2f}",
    ]


def main() -> None:
    prices = pd.read_csv(DATA_PATH)["close"]
    config = BacktestConfig(
        initial_balance=1000,
        base_wager=10,
        threshold_pct=1.5,
        loss_multiplier=2.0,
        max_loss_streak=6,
    )

    results, summary = run_backtest(prices, config)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(RESULTS_PATH, index=False)

    print("Backtest summary")
    print("----------------")
    for line in format_summary(summary):
        print(line)
    print(f"\nTrade-level results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
