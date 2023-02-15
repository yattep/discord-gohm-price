from datetime import datetime, timedelta

PRICE_UPDATE_INTERVAL = 10 # in minutes
GENERIC_UPDATE_INTERVAL = 10 # in minutes
LB_UPDATE_INTERVAL = 720 # in minutes
SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/olympusdao/olympus-protocol-metrics'
ARBI_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/olympusdao/protocol-metrics-arbitrum'
POLY_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/olympusdao/protocol-metrics-polygon'
FTM_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/olympusdao/protocol-metrics-fantom'
BLOCK_REQUEST_QUERY = {"query": "{ tokenRecords(first: 1, orderBy: block, orderDirection: desc) { block }}"}
TOKEN_SUPPLY_QUERY = "{{tokenSupplies( where: {{block: \"{}\"}}) {{ type supplyBalance }}}}"
TOKEN_RECORD_QUERY = "{{tokenRecords( where: {{block: \"{}\"}}) {{ value valueExcludingOhm tokenAddress token isLiquid category multiplier }}}}"
INDEX_PRICE_QUERY = "{{protocolMetrics(first: 1, where: {{block: \"{}\"}}) {{ currentIndex ohmPrice gOhmPrice }}}}"
ADMIN_ROLE = "Scholars"
GRASSHOPPER = "Grasshoppers"
DATE_FORMAT = '%m/%d %-I:%M%p'
LOG_CHANNEL = 825084057700139049
GENERAL_CHANNEL = 823623103874990091
OT_CHANNEL = 798371943324844042
LEARN_CHANNEL = 817567648451133461
EXPIRATION = 120

def get_token_record_7d_query():
    today = datetime.utcnow().date()
    date_7d_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    return {"query": f"{{tokenRecords( where: {{date_gt: \"{date_7d_ago}\"}}, orderBy: block, orderDirection: desc, first: 1000 ) {{ block valueExcludingOhm token isLiquid date }}}}"}

def get_token_supply_7d_query():
    today = datetime.utcnow().date()
    date_7d_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    return {"query": f"{{tokenSupplies( where: {{date_gt: \"{date_7d_ago}\"}}, orderBy: block, orderDirection: desc, first: 1000) {{ type date supplyBalance tokenAddress source sourceAddress pool poolAddress }}}}"}