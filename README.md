# Portfolio AI

AI-powered investment portfolio analysis CLI tool.

Analyze US and Korean stock portfolios with financial metrics, AI-generated insights, and Excel export.

## Features

- **Portfolio Import**: CSV and Excel file support (UTF-8 and CP949 encoding)
- **Financial Metrics**: Total return, annualized return, volatility, Sharpe ratio, max drawdown, beta, alpha
- **AI Insights**: Claude-powered portfolio analysis in Korean (optional)
- **Rebalancing**: Calculate orders to reach target weights with tax estimation
- **Excel Export**: Multi-sheet output (Summary, Holdings, Metrics, Insights)
- **Market Support**: US tickers (AAPL, MSFT) and Korean tickers (005930.KS, 035720.KQ)

## Installation

```bash
# Clone and setup
git clone <repo-url>
cd asset_adviser
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install
pip install -e ".[dev]"
```

## Configuration

```bash
# Copy env template
cp .env.example .env

# Set your Anthropic API key (optional, for AI insights)
# Edit .env and set ANTHROPIC_API_KEY=your-key-here
```

## Usage

### Analyze a Portfolio

```bash
# US portfolio with SPY benchmark
portfolio-ai analyze data/samples/us_tech_portfolio.csv --benchmark SPY

# Korean portfolio with KOSPI benchmark
portfolio-ai analyze data/samples/kr_blue_chip.csv --currency KRW --benchmark ^KS11

# Without AI insights
portfolio-ai analyze data/samples/us_tech_portfolio.csv --no-ai

# Export to Excel
portfolio-ai analyze data/samples/us_tech_portfolio.csv --export output.xlsx --no-ai
```

### Rebalance a Portfolio

Create a target weights CSV:

```csv
ticker,weight
AAPL,30.0
MSFT,30.0
GOOGL,20.0
NVDA,10.0
META,10.0
```

```bash
# Basic rebalance
portfolio-ai rebalance data/samples/us_tech_portfolio.csv --target target.csv

# With tolerance and tax rate
portfolio-ai rebalance data/samples/us_tech_portfolio.csv \
  --target target.csv \
  --tolerance 2.0 \
  --tax-rate 0.22

# Export rebalance report
portfolio-ai rebalance data/samples/us_tech_portfolio.csv \
  --target target.csv \
  --export rebalance_report.xlsx --no-ai
```

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | My Portfolio | Portfolio name |
| `--currency` | USD | Portfolio currency (USD/KRW) |
| `--benchmark` | SPY | Benchmark ticker |
| `--no-ai` | false | Disable AI insights |
| `--export` | - | Export to Excel file |
| `--tolerance` | 1.0 | Rebalance tolerance (%) |
| `--tax-rate` | 0.0 | Tax rate for gain estimation |

## Portfolio File Format

CSV or Excel with these columns:

| Column | Required | Description |
|--------|----------|-------------|
| ticker | Yes | Stock ticker (AAPL, 005930.KS) |
| name | Yes | Company name |
| quantity | Yes | Number of shares |
| avg_cost | Yes | Average purchase price |
| currency | No | Per-holding currency override |

## Development

```bash
# Run tests
pytest tests/ -v --cov

# Run specific test file
pytest tests/test_models.py -v
```

## Tech Stack

- Python 3.12+
- pandas, numpy, yfinance, openpyxl
- anthropic (Claude API)
- click (CLI framework)
- pytest (testing)
