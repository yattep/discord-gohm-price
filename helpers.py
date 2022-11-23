import requests
import constants
import json
## HELPERS

def get_data(url, queryFormat, construct = False):
    if construct:
        query = { "query": queryFormat.format(get_latest_block()) }
    else:
        query = queryFormat
    raw = requests.post(url, json = query)
    raw_json = json.loads(raw.text)
    return raw_json

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '${}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                               ['', 'K', 'M', 'B', 'T'][magnitude])

def get_latest_block():
    data = get_data(constants.SUBGRAPH_URL, constants.BLOCK_REQUEST_QUERY)
    
    return data['data']['tokenRecords'][0]['block']


def get_price_ohm():
    data = get_data(constants.SUBGRAPH_URL, constants.INDEX_PRICE_QUERY, True)
    
    return float(data["data"]["protocolMetrics"][0]["ohmPrice"])

def get_price_gohm():
    data = get_data(constants.SUBGRAPH_URL, constants.INDEX_PRICE_QUERY, True)
    
    return float(data["data"]["protocolMetrics"][0]["gOhmPrice"])

def get_circulating_supply():
    data = get_data(constants.SUBGRAPH_URL,constants.TOKEN_SUPPLY_QUERY, True)
    tokens = data['data']['tokenSupplies']
    non_liq_tkns = list(filter(lambda x: x['type'] != "Liquidity", tokens))
    
    return sum(float(tkn['supplyBalance']) for tkn in non_liq_tkns)

def get_raw_index():
    data = get_data(constants.SUBGRAPH_URL, constants.INDEX_PRICE_QUERY, True)
    
    return data["data"]["protocolMetrics"][0]["currentIndex"]