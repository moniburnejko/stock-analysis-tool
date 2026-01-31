# Stock Analysis Tool
### Python • yFinance API • Data Visualization • Technical Analysis

A Python-based stock market analysis tool.
It fetches financial data from Yahoo Finance, calculates technical indicators (daily returns and moving averages), generates charts, exports results, and summarizes key metrics.

## 📁 Repository Structure
```
stock-analysis-tool/
├── src/
│   └── stock_analysis_tool/
│       ├── __init__.py         # package initialization
│       └── stock_analysis.py   # core analysis module
├── run_analysis.py             # command-line entry point
├── requirements.txt            # python dependencies
├── README.md                   # project overview (this file)
├── .gitignore                  # git ignore rules
├── LICENSE                     # MIT license
├── examples/                   # example outputs
│   └── AMZN_price_sma.png
└── stock_data/                 # generated data (gitignored)
    ├── AMZN.csv
    └── AMZN_price_sma.png
```

## Quick Start
### Installation
1. **Clone the repository**
```bash
git clone https://github.com/moniburnejko/stock-analysis-tool.git
cd stock-analysis-tool
```
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
3. **Run the analysis**
```bash
python run_analysis.py
```
    
### Example Workflows
**Example 1 - Analyze Amazon with default parameters**
```python
from stock_analysis_tool import Config, run_analysis

cfg = Config()  # default: ticker='AMZN', period='5y', interval='1d', sma_window=20
df, stats = run_analysis(cfg)
```

**Example 2 - Change ticker and period**
```python
from stock_analysis_tool import Config, run_analysis

cfg = Config(ticker='AAPL', period='2y')
df, stats = run_analysis(cfg)
```

**Example 3 - Weekly analysis with longer SMA**
```python
from stock_analysis_tool import Config, run_analysis

cfg = Config(
    ticker='TSLA',
    period='max',
    interval='1wk',
    sma_window=100,
    show_plots=True
)
df, stats = run_analysis(cfg)
```

**Example 4 - Multi-stock analysis**
```python
from stock_analysis_tool import Config, run_analysis

tickers = ['ORCL', 'NVDA', 'MSFT', 'IBM']

for ticker in tickers:
    cfg = Config(ticker=ticker, period='2y', sma_window=50)
    df, stats = run_analysis(cfg)
```

## Output Examples
### Generated Statistics
|                    | Value       |
|------------------------|-------------|
| Rows                   | 1256.0      |
| Start Date             | 2020-10-26  |
| End Date               | 2025-10-24  |
| Start Price            | 160.35      |
| End Price              | 224.21      |
| Total Return (%)       | 39.82       |
| Daily Return Mean (%)  | 0.05        |
| Daily Return Std (%)   | 2.21        |
| Min Price              | 81.82       |
| Max Price              | 242.06      |

### Sample Visualization
*Price chart with 20-day simple moving average overlay*

![example chart](examples/AMZN_price_sma.png)

## Technologies
- **Python 3.14+** - core programming language
- **pandas** - data manipulation and analysis
- **yfinance** - Yahoo Finance API wrapper
- **matplotlib** - data visualization
- **numpy** - numerical computing

## Advanced Features
### Available Functions
- `fetch_prices()` - download historical stock data
- `add_metrics()` - calculate technical indicators
- `save_csv()` - export data to CSV
- `plot_price_sma()` - generate price charts
- `summarize()` - compute statistical summary
- `run_analysis()` - complete analysis pipeline

### Error Handling
The tool includes robust error handling for:
- invalid ticker symbols
- network failures
- missing data
- empty datasets

```python
from stock_analysis_tool import Config, run_analysis

try:
    cfg = Config(ticker='INVALID')
    df, stats = run_analysis(cfg)
except RuntimeError as e:
    print(f"Analysis failed: {e}")
```

## API Reference
### Config Class
```python
@dataclass
class Config:
    """Configuration for stock analysis parameters"""
    ticker: str = 'AMZN'
    period: str = '5y'
    interval: str = '1d'
    sma_window: int = 20
    out_dir: Path = Path('stock_data')
    show_plots: bool = True
```

### Core Functions
```python
def fetch_prices(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """Fetch historical stock prices from Yahoo Finance"""
    
def add_metrics(df: pd.DataFrame, sma_window: int) -> pd.DataFrame:
    """Add technical indicators (SMA, returns) to dataframe"""
    
def run_analysis(cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute complete analysis workflow"""
```

## Acknowledgments
- Data provided by [Yahoo Finance](https://finance.yahoo.com/)
- Built with [yfinance](https://github.com/ranaroussi/yfinance) library
- Inspired by my assignment from the IBM Data Analyst Professional Certificate program. It has been significantly extended, refactored, and automated to serve as a fully functional and reproducible portfolio project

## License
This project is released under the **MIT License**.  

## Connect
👩‍💻 **Monika Burnejko**  
*Data Analyst in Training | Python • Pandas • yFinance • Data Viz*

📧 [moniburnejko@gmail.com](mailto:moniburnejko@gmail.com)  
💼 [LinkedIn](https://www.linkedin.com/in/monika-burnejko-9301a1357)  
🌐 [Portfolio](https://www.notion.so/monikaburnejko/Data-Analytics-Portfolio-2761bac67ca9807298aee038976f0085?pvs=9)

---
<p align="center">
🌟 if you found this project helpful, please consider giving it a star! 🌟
</p>
