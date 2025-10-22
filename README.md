# Stock Basket Cointegration Analysis

## Project Overview

This project aims to identify a basket of stocks where each individual stock is cointegrated with the larger basket, enabling the detection of statistically meaningful price action divergences.

## Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Cointegration
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

6. Run the analysis:
```bash
cd data
python main.py
```

For a quick start with enhanced features, see [QUICK_START.md](QUICK_START.md).

## Project Goals

The primary objective is to **identify when a stock's price action diverges from the basket's in a statistically meaningful way**. This approach differs from traditional pairs trading or statistical arbitrage strategies - instead, it focuses on:

- Building a cohesive basket of stocks with strong cointegration relationships
- Detecting when individual stocks break away from the basket's long-term equilibrium
- Providing statistical signals for potential divergence events

## Current Analysis

### Stock Universe
I want to try to focus on baskets of stocks similar to the ones below:

- Enterprise software (CRM, NOW, WDAY, HUBS)
- Cloud infrastructure (SNOW, NET, DDOG, CFLT)
- Development platforms (TEAM, GOOGL, META)
- Security companies (CRWD, ZS)
- And other tech/cloud companies

### Methodology