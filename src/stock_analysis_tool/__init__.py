"""Stock Analysis Tool - A Python tool for analyzing stock market data."""

from .stock_analysis import (
    Config,
    fetch_prices,
    add_metrics,
    save_csv,
    plot_price_sma,
    summarize,
    run_analysis,
)

__all__ = [
    "Config",
    "fetch_prices",
    "add_metrics",
    "save_csv",
    "plot_price_sma",
    "summarize",
    "run_analysis",
]
