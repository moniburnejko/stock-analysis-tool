from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd
import yfinance as yf


# centralized theme to keep plots consistent and decoupled from matplotlib defaults
PLOT_THEME = {
    "figure.facecolor": "#0F1B2B",
    "axes.facecolor": "#0F1B2B",
    "axes.edgecolor": "#2A3A55",
    "axes.labelcolor": "#C8D6F0",
    "xtick.color": "#9FB4D0",
    "ytick.color": "#9FB4D0",
    "text.color": "#C8D6F0",
    "grid.color": "#22324A",
    "grid.alpha": 0.6,
    "grid.linestyle": "--",
    "font.family": "Roboto",
    "axes.titleweight": "bold",
}


@dataclass
class Config:
    ticker: str = "AMZN"
    period: str = "5y"
    interval: str = "1d"
    sma_window: int = 20
    out_dir: Path = Path("stock_data")
    show_plots: bool = True

    def ensure_out_dir(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)


def fetch_prices(
    ticker: str,
    period: str,
    interval: str,
    downloader: Callable[..., pd.DataFrame | None] = yf.download,
) -> pd.DataFrame:
    df = downloader(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )
    if df is None:
        raise RuntimeError(f"No data returned for ticker {ticker}")
    if df.empty:
        raise RuntimeError(f"No data found for ticker {ticker}")

    df = df.dropna(how="all")
    if df.empty:
        raise RuntimeError(f"All data was NaN for ticker {ticker}")

    df = df.sort_index()  # ensure deterministic start/end stats and plotting
    df.index.name = "Date"
    return df


def get_close(df: pd.DataFrame) -> pd.Series:
    """Prefer adjusted close; fall back to close when needed."""
    if "Adj Close" in df.columns:
        if "Close" in df.columns:
            return df["Adj Close"].fillna(df["Close"])
        return df["Adj Close"]
    if "Close" in df.columns:
        return df["Close"]
    raise KeyError("Expected 'Adj Close' or 'Close' column in data")


def add_metrics(df: pd.DataFrame, sma_window: int) -> pd.DataFrame:
    out = df.copy()
    close = get_close(out).ffill()  # make pct_change behavior explicit
    out["return_daily"] = close.pct_change()
    out[f"SMA_{sma_window}"] = close.rolling(sma_window).mean()

    return out


def save_csv(df: pd.DataFrame, ticker: str, cfg: Config) -> Path:
    path = cfg.out_dir / f"{ticker}.csv"

    df.to_csv(path)

    return path


def plot_price_sma(df: pd.DataFrame, ticker: str, sma_window: int, cfg: Config) -> Path:
    close = get_close(df)
    sma_col = f"SMA_{sma_window}"
    sma = df[sma_col]

    out_path = cfg.out_dir / f"{ticker}_price_sma.png"

    with plt.rc_context(PLOT_THEME):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(
            close.index, close.values, label="Price", linewidth=1.8, color="#7AD9C7"
        )
        ax.plot(
            df.index,
            sma,
            label=f"SMA {sma_window}",
            linewidth=1.6,
            alpha=0.9,
            color="#D16F60",
        )
        ax.set(
            title=f"{ticker} - Price & SMA",
            xlabel="Date",
            ylabel="Price (USD)",
        )
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.2f}"))
        locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        ax.legend(frameon=False, ncol=2)
        ax.grid(True, which="major")
        fig.tight_layout()

        fig.savefig(out_path, dpi=150)

        if cfg.show_plots:
            plt.show()

        plt.close(fig)

    return out_path


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    close: pd.Series = get_close(df)

    returns = df["return_daily"].dropna()

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


def run_analysis(cfg: Config) -> None:
    print(
        f"[INFO] Analyzing {cfg.ticker} | "
        f"Period: {cfg.period} | "
        f"Interval: {cfg.interval}"
    )

    try:
        df = fetch_prices(cfg.ticker, cfg.period, cfg.interval)

        cfg.ensure_out_dir()

        df = add_metrics(df, cfg.sma_window)
        csv_path = save_csv(df, cfg.ticker, cfg)
        print(f"[OK] Saved: {csv_path}")

        png_path = plot_price_sma(df, cfg.ticker, cfg.sma_window, cfg)
        print(f"[OK] Saved: {png_path}")

        stats = summarize(df)

        print(stats)

    except (RuntimeError, KeyError, ValueError) as e:
        print(f"[ERROR] {e}")


def main() -> None:
    config = Config()
    run_analysis(config)


if __name__ == "__main__":
    main()
