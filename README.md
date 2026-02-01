## stock analysis tool 💸

minimal script for pulling market data from yahoo finance (`yfinance`), computing a few basics (daily return + sma), and exporting a csv + a clean, dark chart.

---

### what the script does

- downloads price history via `yfinance`
- normalizes a close series (prefers adjusted close; falls back to close)
- adds:
  - `return_daily`
  - `sma_<window>`
- saves csv + png
- prints a small summary table (date range, min/max, total return, daily mean/std)

---
### plot style

the look is controlled by `PLOT_THEME` in `src/stock_analysis.py` (dark, trading-ish palette). the goal is readability without noise: clean lines, calm grid, consistent colors.

---

### output

output files are written into `stock_data/`:

- `stock_data/<ticker>.csv` (raw data + `return_daily` and `sma_<window>`)
- `stock_data/<ticker>_price_sma.png` (price + sma chart)
---

### tooling

- `uv`: env + installs + running commands
- `ty`: type checking
- `ruff`: linting + formatting
- `pytest`: tests
---

### quick start

#### clone

```bash
git clone https://github.com/moniburnejko/stock-analysis-tool.git
cd stock-analysis-tool
```
---
#### setup (uv)

pin python for this repo (optional but recommended):

```bash
uv python pin 3.14
```

create/sync the venv + install dev tools:

```bash
uv sync --dev
```
---
#### run

`config` defaults live in `src/stock_analysis.py`.

```bash
uv run python src/stock_analysis.py
```

note: if you prefer module execution, it also works after setup:

```bash
uv run python -m stock_analysis
```

---

### workflows (examples)

the script is intentionally cli-light; each workflow below shows two options: (a) quick code tweak, (b) terminal command.

#### 1) change ticker + period

option a: edit `src/stock_analysis.py` (in `main()`)

```python
config = Config(ticker="aapl", period="1y")
run_analysis(config)
```

option b: terminal

```bash
uv run python -c 'from stock_analysis import Config, run_analysis; run_analysis(Config(ticker="aapl", period="1y"))'
```

#### 2) weekly analysis with longer sma

option a: edit `src/stock_analysis.py` (in `main()`)

```python
config = Config(ticker="amzn", period="10y", interval="1wk", sma_window=50)
run_analysis(config)
```

option b: terminal

```bash
uv run python -c 'from stock_analysis import Config, run_analysis; run_analysis(Config(ticker="amzn", period="10y", interval="1wk", sma_window=50))'
```

#### 3) multi-stock analysis (4 tickers)

option a: edit `src/stock_analysis.py` (in `main()`)

```python
for t in ["amzn", "aapl", "msft", "nvda"]:
    run_analysis(Config(ticker=t, period="2y"))
```

option b: terminal

```bash
uv run python -c 'from stock_analysis import Config, run_analysis; [run_analysis(Config(ticker=t, period="2y")) for t in ["amzn","aapl","msft","nvda"]]'
```

---

### tests (pytest)

```bash
uv run python -m pytest
```

### checks

```bash
uv run ty check
uv run ruff check .
uv run ruff format .
```

---

### note

this project was inspired by a small ibm data analyst course assignment. i first turned it into a standalone script, and later gave it a proper refresh with newer, commonly used tooling and cleaner patterns.

---

### 💌 let’s connect!

[![email](https://img.shields.io/badge/email-FFB6C1?style=for-the-badge&logo=gmail&logoColor=424B54)](mailto:moniburnejko@gmail.com)
[![linkedin](https://img.shields.io/badge/linkedin-FFB6C1?style=for-the-badge&logo=linkedin&logoColor=424B54)](https://www.linkedin.com/in/monika-burnejko-9301a1357)
[![kaggle](https://img.shields.io/badge/kaggle-FFB6C1?style=for-the-badge&logo=kaggle&logoColor=424B54e)](https://www.kaggle.com/monikaburnejko)
