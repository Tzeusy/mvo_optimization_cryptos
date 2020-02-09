# Mean-Variance Optimization for Cryptocurrencies
Applying Markowitz Mean Variance Optimization to obtain optimal allocation for specified cryptocurrencies using a two-week history of hourly prices

## Installation
Runs on Python 3.7. Install all dependencies, as found in `requirements.txt`.
```python3 -m pip install -r requirements.txt```

## Running
From the cloned directory, run `python3 main.py`

## Overview
Running `main.py` creates a vector of weights for the portfolio using mean-variance portfolio optimization, given a set of target weights. Cryptocurrencies for which to analyze are currently preset to BTC, LTC, and XRP.

The 'Markowitz Bullet' is generated by generating random portfolios; convex optimization is used to attain a set of optimal weights (maximizing return wrt. stddev) for each target stddev.