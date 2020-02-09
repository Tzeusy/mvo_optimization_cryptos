import datetime
import copy
import matplotlib.pyplot as plt
import pprint
import pandas as pd
import json

from data_utils import get_trade_history, get_contract_details
from mv_optimize import random_weight_generator, generate_random_portfolio_stats, optimal_weight_vector

# Get data regarding the contracts, via Huobi's contract_contract_info endpoint
pp = pprint.PrettyPrinter(indent=4)
BASE_URL = 'https://api.hbdm.com'

def plot_efficient_frontier(ret_df, risks, returns):
    n_portfolios = 1000
    means, stds = [], []
    for i in range(n_portfolios):
        port_ret, port_std = generate_random_portfolio_stats(ret_df)
        means.append(port_ret[0, 0])
        stds.append(port_std[0, 0])
    plt.title(f'Mean Returns vs Standard Deviation for {n_portfolios} randomly generated portfolios')
    plt.ylabel('mean')  
    plt.xlabel('std')  
    plt.plot(stds, means, 'o', label=f"{n_portfolios}s returns/stddev profiles ")
    plt.plot(risks, returns, 'y-o', label='Efficient Frontier')
    plt.show()

def merge_crypto_price_data(price_df, ret_df, crypto_data, crypto_name):
    for entry in crypto_data:
        entry['datetime'] = datetime.datetime.fromtimestamp(entry['id'])
    # crypto_data = [entry for entry in crypto_data if entry['datetime'] >= start_datetime]
    crypto_df = pd.DataFrame(crypto_data)
    crypto_df.set_index('datetime', inplace=True)
    crypto_df['returns'] = crypto_df.close.pct_change() * 100
    price_df[f'{crypto_name}_close'] = crypto_df['close']
    ret_df[f'{crypto_name}_returns'] = crypto_df['returns']
    return price_df, ret_df

def initialize_dfs(lookback_days=15, period=60):
    """Initializes DataFrames as necessary with start and end datetimes set accordingly, intervalized by {period}
    
    Arguments:
        lookback_days {int} -- Number of days to look back in history
        freq {int} -- Number of minutes between entries to request: Must be in [1, 5, 15, 30, 60]
    
    Returns:
        (DataFrame, DataFrame) -- DataFrames with indices set to specified period
    """    
    price_df = pd.DataFrame()
    start_datetime = (datetime.datetime.now() - datetime.timedelta(days=lookback_days)).replace(hour=4, minute=0, second=0, microsecond=0)
    end_datetime = (datetime.datetime.now() - datetime.timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)
    price_df['datetime'] = pd.date_range(start=start_datetime, end=end_datetime, freq=f'{period}min')
    price_df.set_index('datetime', inplace=True)
    ret_df = copy.deepcopy(price_df)
    return price_df, ret_df

def main(cryptocurrencies):
    # contracts_of_interest = ['BTC1227', 'XRP1227', 'LTC1227']  # Nonexistent, presumably archived on Huobi's end
    contracts_of_interest = [f'{crypto}200221' for crypto in cryptocurrencies]

    contract_details = {
        contract:get_contract_details(BASE_URL, contract)['data'] for contract in contracts_of_interest
    }

    price_df, ret_df = initialize_dfs(lookback_days=15, period=60)
    for cryptocurrency in ['BTC', 'LTC', 'XRP']:
        kline_data = get_trade_history(BASE_URL, cryptocurrency).json()['data']
        price_df, ret_df = merge_crypto_price_data(price_df, ret_df, kline_data, cryptocurrency)  # Price df just for plotting if wanted
    
    weights, returns, risks, return_weight_mapping = optimal_weight_vector(ret_df, cryptocurrencies)
    plot_efficient_frontier(ret_df, risks, returns)
    print("Optimal weights for relevant returns:")
    pp.pprint(return_weight_mapping)
    with open(f"{'_'.join(cryptocurrencies)}.json", 'w') as f:
        json.dump(return_weight_mapping, f)
    return weights


if __name__ == '__main__':
    cryptocurrencies = ['BTC', 'LTC', 'XRP']
    main(cryptocurrencies)