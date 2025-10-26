from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


@dataclass
class Config:
# stock ticker symbol and data range
    ticker: str = 'AMZN'
    period: str = '5y'      # e.g., '1y', '2y', '5y', 'ytd'
    interval: str = '1d'    # e.g., '1d', '1wk', '1mo'
# indicators and output
    sma_window: int = 20
    out_dir: Path = Path('stock_data')
    show_plots: bool = True
 
    def ensure_out_dir(self) -> None:
        """ 
		create output directory if it doesn't exist 
		
		creates the directory specified in out_dir attribute, including
        any necessary parent directories.
		"""
        self.out_dir.mkdir(parents=True, exist_ok=True)


def fetch_prices(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """ 
	fetch historical stock price data from yahoo finance.
	
	downloads ohlcv (open, high, low, close, volume) data for the specified
    ticker symbol and time period using the yfinance library.
	"""    
    try:
        ## group_by='column' ensures a flat column index for recent yfinance
        df = yf.download(ticker, period=period, interval=interval,
                         auto_adjust=False, progress=False, group_by='column')
        if df.empty:
            raise RuntimeError(f'No data found for ticker {ticker}')
            
        # drop all-nan rows and set a clean index name
        df = df.dropna(how='all')
        if df.empty:
            raise RuntimeError(f'All data was NaN for ticker {ticker}')
        df.index.name = 'Date'
        return df
    except Exception as e:
        raise RuntimeError(f'Failed to fetch data for {ticker}: {e}')


def add_metrics(df: pd.DataFrame, sma_window: int) -> pd.DataFrame:
    """ 
	add technical indicators and metrics to the price dataframe.
    
    calculates and adds the following columns:
    - daily returns (percentage change)
    - simple moving average (sma)
	"""
    out = df.copy() # work on a copy to avoid mutating the original
    close = out['Adj Close'].fillna(out['Close'])
    
    # daily percentage change
    out['return_daily'] = close.pct_change()
    
    # simple moving average
    out[f'SMA_{sma_window}'] = close.rolling(sma_window).mean()
    return out


def save_csv(df: pd.DataFrame, ticker: str, cfg: Config) -> Path:
    """
	save dataframe to csv file.

	saves the dataframe to a csv file in the configured output directory.
    creates the output directory if it doesn't exist.
	""" 
    cfg.ensure_out_dir()
    path = cfg.out_dir / f'{ticker}.csv'
    df.to_csv(path)
    return path


def plot_price_sma(df: pd.DataFrame, ticker: str, sma_window: int, cfg: Config) -> Path:
    """
	generate and save a price chart with simple moving average overlay.
    
    creates a line plot showing the stock's closing price and its sma.
    the plot is saved as a png file and optionally displayed in the notebook.
	"""
    cfg.ensure_out_dir()
    close = df['Adj Close'].fillna(df['Close'])

    # render a line chart for price and sma
    plt.figure(figsize=(10, 5))
    plt.plot(close.index, close.values, label='Price', linewidth=1.5)
    plt.plot(df.index, df[f'SMA_{sma_window}'], label=f'SMA {sma_window}', alpha=0.7)
    plt.title(f'{ticker} - Price & SMA')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    # save the plot as a png file and optionally displayed in the notebook
    out_path = cfg.out_dir / f'{ticker}_price_sma.png'
    plt.savefig(out_path, dpi=150)
    if cfg.show_plots:
        plt.show()
    plt.close()
    return out_path


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """
    generate statistical summary of stock price data.
    
    calculates key statistics including:
    - dataset size (number of rows)
    - date range (start and end dates)
    - price range (min and max)
    - total return over the period
    - daily return statistics (mean and standard deviation)
	
	prefer adjusted close if available.
	""" 
    if 'Adj Close' in df.columns:
        close = df['Adj Close'].squeeze()
    else:
        close = df['Close'].squeeze()

    returns = df['return_daily'].dropna()

    stats = {
        'Rows': len(df),
        'Start Date': df.index[0].strftime('%Y-%m-%d'),
        'End Date': df.index[-1].strftime('%Y-%m-%d'),
        'Start Price': float(close.iloc[0]),
        'End Price': float(close.iloc[-1]),
        'Total Return (%)': float(((close.iloc[-1]) / (close.iloc[0]) - 1) * 100),
        'Daily Return Mean (%)': returns.mean() * 100,
        'Daily Return Std (%)': returns.std() * 100,
        'Min Price': float(close.min()),
        'Max Price': float(close.max())
    }

    return pd.DataFrame([stats]).T.rename(columns={0: 'Value'}).round(2)


def run_analysis(cfg: Config):
    """ 
	execute complete stock analysis workflow.
	""" 
    print(f'[INFO] Analyzing {cfg.ticker} | Period: {cfg.period} | Interval: {cfg.interval}')
    df = fetch_prices(cfg.ticker, cfg.period, cfg.interval)
    df = add_metrics(df, cfg.sma_window)
    csv_path = save_csv(df, cfg.ticker, cfg)
    png_path = plot_price_sma(df, cfg.ticker, cfg.sma_window, cfg)
    stats = summarize(df)
    print(f'[OK] Saved: {csv_path}')
    print(f'[OK] Saved: {png_path}')
    display(stats)  
    return df, stats