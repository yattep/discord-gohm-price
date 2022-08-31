import requests
import constants
import json
## HELPERS

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '${}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                               ['', 'K', 'M', 'B', 'T'][magnitude])

def get_latest_block():
    block_raw = requests.post(constants.SUBGRAPH_URL, json = constants.BLOCK_REQUEST_QUERY)
    block_json = json.loads(block_raw.text)
    return block_json['data']['tokenRecords'][0]['block']


def get_ohm_price():
    query = {"query": constants.INDEX_PRICE_QUERY.format(get_latest_block())}
    raw_price_data = requests.post(constants.SUBGRAPH_URL, json = query)
    raw_price_json_data = json.loads(raw_price_data.text)
    return float(raw_price_json_data["data"]["protocolMetrics"][0]["ohmPrice"])

def get_circulating_supply():
    query = {"query": constants.TOKEN_SUPPLY_QUERY.format(get_latest_block())}
    raw_tsupply_data = requests.post(constants.SUBGRAPH_URL, json = query)
    raw_tsupply_json_data = json.loads(raw_tsupply_data.text)
    tokens = raw_tsupply_json_data['data']['tokenSupplies']
    non_liq_tkns = list(filter(lambda x: x['type'] != "Liquidity", tokens))
    return sum(float(t['supplyBalance']) for t in non_liq_tkns)

def get_raw_index():
    query = {"query": constants.INDEX_PRICE_QUERY.format(get_latest_block())}
    raw_data = requests.post(constants.SUBGRAPH_URL, json = query)
    json_data = json.loads(raw_data.text)
    return json_data["data"]["protocolMetrics"][0]["currentIndex"]