from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class BacktestConfig:
    initial_balance: float = 1000.0
    base_wager: float = 10.0
    threshold_pct: float = 1.5
    loss_multiplier: float = 2.0
    max_loss_streak: int = 6


def _max_drawdown(equity: pd.Series) -> tuple[float, float]:
    running_peak = equity.cummax()
    drawdown = equity - running_peak
    drawdown_pct = (equity / running_peak - 1) * 100
    return float(drawdown.min()), float(drawdown_pct.min())


def run_backtest(prices: Iterable[float], config: BacktestConfig) -> tuple[pd.DataFrame, dict]:
    price_list = [float(price) for price in prices]
    if len(price_list) < 2:
        raise ValueError("At least two prices are required.")
    if config.threshold_pct <= 0:
        raise ValueError("threshold_pct must be greater than zero.")

    balance = config.initial_balance
    wager = config.base_wager
    direction = "LONG"
    loss_streak = 0
    entry_index = 0
    trades: list[dict] = []

    while entry_index < len(price_list) - 1:
        entry_price = price_list[entry_index]
        exit_index = None
        outcome = None
        move_pct = None

        for idx in range(entry_index + 1, len(price_list)):
            move = (price_list[idx] - entry_price) / entry_price * 100
            if abs(move) >= config.threshold_pct:
                exit_index = idx
                move_pct = move
                if direction == "LONG":
                    outcome = "WIN" if move > 0 else "LOSS"
                else:
                    outcome = "WIN" if move < 0 else "LOSS"
                break

        if exit_index is None:
            break

        pnl = wager if outcome == "WIN" else -wager
        balance += pnl

        trades.append(
            {
                "trade": len(trades) + 1,
                "direction": direction,
                "entry_index": entry_index,
                "exit_index": exit_index,
                "entry_price": entry_price,
                "exit_price": price_list[exit_index],
                "move_pct": round(move_pct, 3),
                "outcome": outcome,
                "wager": round(wager, 2),
                "pnl": round(pnl, 2),
                "balance": round(balance, 2),
            }
        )

        if outcome == "WIN":
            loss_streak = 0
            wager = config.base_wager
        else:
            loss_streak += 1
            wager *= config.loss_multiplier
            direction = "SHORT" if direction == "LONG" else "LONG"

        if balance <= 0 or loss_streak >= config.max_loss_streak:
            break

        entry_index = exit_index

    results = pd.DataFrame(trades)
    if results.empty:
        summary = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "net_pnl": 0.0,
            "return_pct": 0.0,
            "profit_factor": 0.0,
            "final_balance": config.initial_balance,
            "max_drawdown": 0.0,
            "max_drawdown_pct": 0.0,
            "max_wager": config.base_wager,
        }
        return results, summary

    wins = int((results["outcome"] == "WIN").sum())
    losses = int((results["outcome"] == "LOSS").sum())
    gross_profit = float(results.loc[results["pnl"] > 0, "pnl"].sum())
    gross_loss = abs(float(results.loc[results["pnl"] < 0, "pnl"].sum()))
    final_balance = float(results["balance"].iloc[-1])
    max_drawdown, max_drawdown_pct = _max_drawdown(results["balance"])

    summary = {
        "total_trades": int(len(results)),
        "winning_trades": wins,
        "losing_trades": losses,
        "win_rate": round(wins / len(results) * 100, 2),
        "net_pnl": round(float(results["pnl"].sum()), 2),
        "return_pct": round((final_balance / config.initial_balance - 1) * 100, 2),
        "profit_factor": round(gross_profit / gross_loss, 2) if gross_loss else float("inf"),
        "final_balance": round(final_balance, 2),
        "max_drawdown": round(max_drawdown, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "max_wager": round(float(results["wager"].max()), 2),
    }
    return results, summary
