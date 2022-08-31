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

async def get_ohm_price():
    price_query = {"query": constants.INDEX_REQUEST_OBJ}
    raw_price_data = requests.post(constants.SUBGRAPH_URL, json = price_query)
    raw_price_json_data = json.loads(raw_price_data.text)
    print(raw_price_json_data)
    return float(raw_price_json_data["data"]["protocolMetrics"][0]["ohmPrice"])

async def get_circulating_supply():
    supply_query = {"query": constants.TSUPPLY_REQUEST_OBJ}
    raw_tsupply_data = requests.post(constants.SUBGRAPH_URL, json = supply_query)
    raw_tsupply_json_data = json.loads(raw_tsupply_data.text)
    tokens = raw_tsupply_json_data['data']['tokenSupplies']
    non_liq_tkns = list(filter(lambda x: x['type'] != "Liquidity", tokens))
    print(non_liq_tkns)
    return sum(float(t['supplyBalance']) for t in non_liq_tkns)

async def get_raw_index():
    index_query = {"query": constants.INDEX_REQUEST_OBJ}
    raw_data = requests.post(constants.SUBGRAPH_URL, json = index_query)
    json_data = json.loads(raw_data.text)
    print(json_data)
    return json_data["data"]["protocolMetrics"][0]["currentIndex"]