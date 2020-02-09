import requests
import urllib
import json

def get_contract_details(base_url, contract_code):
    params = {}
    params['contract_code'] = contract_code
    postdata = urllib.parse.urlencode(params)

    contract_info = f'{base_url}/api/v1/contract_contract_info'
    response = requests.get(contract_info, postdata, headers=params)
    if response.status_code != 200 or not response.ok:
        return False
    return response.json()

def get_trade_history(base_url, cryptocurrency):
    """GET request for price history from Huobi's kline API endpoint
    
    Arguments:
        base_url {str} -- Base url for Huobi API
        cryptocurrency {str} -- Cryptocurrency for which to request, eg BTC, LTC, XRP`
    
    Returns:
        {dict} -- JSON file returned by Huobi
    """    
    contract_history_endpoint = f'{base_url}/market/history/kline'
    params = {
        'symbol': f'{cryptocurrency}_CQ',
        'period': '60min',
        'size': 500,
    }
    postdata = urllib.parse.urlencode(params)
    params = json.dumps(params, default=str)
    response = requests.get(contract_history_endpoint, postdata)
    if response.status_code != 200 or not response.ok:
        print('Error! Invalid status code')
        return False
    return response