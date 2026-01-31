"""Stock Analysis Tool - Core functionality for analyzing stock market data.

This module provides tools for fetching, analyzing, and visualizing stock market
data from Yahoo Finance. It includes technical indicators, statistical summaries,
and chart generation.
"""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


@dataclass
class Config:
    """Configuration for stock analysis parameters.

    Attributes:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'AMZN')
        period: Time period for historical data (e.g., '1y', '2y', '5y', 'ytd')
        interval: Data interval (e.g., '1d', '1wk', '1mo')
        sma_window: Window size for simple moving average calculation
        out_dir: Output directory for saving results
        show_plots: Whether to display plots interactively
    """

    ticker: str = "AMZN"
    period: str = "5y"
    interval: str = "1d"
    sma_window: int = 20
    out_dir: Path = Path("stock_data")
    show_plots: bool = True

    def ensure_out_dir(self) -> None:
        """Create output directory if it doesn't exist.

        Creates the directory specified in out_dir attribute, including
        any necessary parent directories.
        """
        self.out_dir.mkdir(parents=True, exist_ok=True)


def fetch_prices(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """Fetch historical stock price data from Yahoo Finance.

    Downloads OHLCV (Open, High, Low, Close, Volume) data for the specified
    ticker symbol and time period using the yfinance library.

    Args:
        ticker: Stock ticker symbol
        period: Time period for data (e.g., '1y', '5y', 'max')
        interval: Data interval (e.g., '1d', '1wk', '1mo')

    Returns:
        DataFrame with historical price data indexed by date

    Raises:
        RuntimeError: If data fetch fails or returns empty dataset
    """
    try:
        # group_by='column' ensures a flat column index for recent yfinance
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            group_by="column",
        )
        if df.empty:
            raise RuntimeError(f"No data found for ticker {ticker}")

        # drop all-nan rows and set a clean index name
        df = df.dropna(how="all")
        if df.empty:
            raise RuntimeError(f"All data was NaN for ticker {ticker}")
        df.index.name = "Date"
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data for {ticker}: {e}") from e


def add_metrics(df: pd.DataFrame, sma_window: int) -> pd.DataFrame:
    """Add technical indicators and metrics to the price dataframe.

    Calculates and adds the following columns:
    - Daily returns (percentage change)
    - Simple moving average (SMA)

    Args:
        df: DataFrame with stock price data
        sma_window: Window size for SMA calculation

    Returns:
        DataFrame with additional metrics columns
    """
    out = df.copy()  # work on a copy to avoid mutating the original
    close = out["Adj Close"].fillna(out["Close"])

    # daily percentage change
    out["return_daily"] = close.pct_change()

    # simple moving average
    out[f"SMA_{sma_window}"] = close.rolling(sma_window).mean()
    return out


def save_csv(df: pd.DataFrame, ticker: str, cfg: Config) -> Path:
    """Save dataframe to CSV file.

    Saves the dataframe to a CSV file in the configured output directory.
    Creates the output directory if it doesn't exist.

    Args:
        df: DataFrame to save
        ticker: Stock ticker symbol (used for filename)
        cfg: Configuration object

    Returns:
        Path to the saved CSV file
    """
    cfg.ensure_out_dir()
    path = cfg.out_dir / f"{ticker}.csv"
    df.to_csv(path)
    return path


def plot_price_sma(df: pd.DataFrame, ticker: str, sma_window: int, cfg: Config) -> Path:
    """Generate and save a price chart with simple moving average overlay.

    Creates a line plot showing the stock's closing price and its SMA.
    The plot is saved as a PNG file and optionally displayed.

    Args:
        df: DataFrame with price data and SMA
        ticker: Stock ticker symbol (used for title and filename)
        sma_window: SMA window size (used for label)
        cfg: Configuration object

    Returns:
        Path to the saved PNG file
    """
    cfg.ensure_out_dir()
    close = df["Adj Close"].fillna(df["Close"])

    # render a line chart for price and sma
    plt.figure(figsize=(10, 5))
    plt.plot(close.index, close.values, label="Price", linewidth=1.5)
    plt.plot(df.index, df[f"SMA_{sma_window}"], label=f"SMA {sma_window}", alpha=0.7)
    plt.title(f"{ticker} - Price & SMA")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    # save the plot as a png file
    out_path = cfg.out_dir / f"{ticker}_price_sma.png"
    plt.savefig(out_path, dpi=150)
    if cfg.show_plots:
        plt.show()
    plt.close()
    return out_path


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Generate statistical summary of stock price data.

    Calculates key statistics including:
    - Dataset size (number of rows)
    - Date range (start and end dates)
    - Price range (min and max)
    - Total return over the period
    - Daily return statistics (mean and standard deviation)

    Args:
        df: DataFrame with price data and metrics

    Returns:
        DataFrame with summary statistics
    """
    close = df.get("Adj Close", df["Close"]).squeeze()
    returns = df["return_daily"].dropna()

    # calculate key statistics
    stats = {
        "Rows": len(df),
        "Start Date": df.index[0].strftime("%Y-%m-%d"),
        "End Date": df.index[-1].strftime("%Y-%m-%d"),
        "Start Price": float(close.iloc[0]),
        "End Price": float(close.iloc[-1]),
        "Total Return (%)": float((close.iloc[-1] / close.iloc[0] - 1) * 100),
        "Daily Return Mean (%)": float(returns.mean() * 100),
        "Daily Return Std (%)": float(returns.std() * 100),
        "Min Price": float(close.min()),
        "Max Price": float(close.max()),
    }

    df_out = pd.DataFrame([stats]).T.rename(columns={0: "Value"})
    nums = pd.to_numeric(df_out["Value"], errors="coerce")
    df_out["Value"] = df_out["Value"].where(nums.isna(), nums.round(2))

    return df_out


def run_analysis(cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute complete stock analysis workflow.

    Performs the following steps:
    1. Fetch historical price data
    2. Calculate technical indicators
    3. Save data to CSV
    4. Generate and save price chart
    5. Calculate and display summary statistics

    Args:
        cfg: Configuration object with analysis parameters

    Returns:
        Tuple of (price dataframe, statistics dataframe)
    """
    print(
        f"[INFO] Analyzing {cfg.ticker} | Period: {cfg.period} | Interval: {cfg.interval}"
    )
    df = fetch_prices(cfg.ticker, cfg.period, cfg.interval)
    df = add_metrics(df, cfg.sma_window)
    csv_path = save_csv(df, cfg.ticker, cfg)
    png_path = plot_price_sma(df, cfg.ticker, cfg.sma_window, cfg)
    stats = summarize(df)

    print(f"[OK] Saved: {csv_path}")
    print(f"[OK] Saved: {png_path}")
    print("\nSummary Statistics:")
    print(stats.to_string())

    return df, stats


def main() -> None:
    """Run stock analysis with default configuration."""
    cfg = Config()
    run_analysis(cfg)


if __name__ == "__main__":
    main()
