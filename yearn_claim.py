import requests, time, json
from web3 import Web3
from utils.logger import log_discord

VAULT_ABI = [
    {"inputs":[],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
]

def list_vaults_for_address(address, alchemy_key=None, moralis_key=None):
    tokens = []
    if moralis_key:
        url = f"https://deep-index.moralis.io/api/v2/{address}/erc20"
        headers = {'X-API-Key': moralis_key, 'accept':'application/json'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            for t in r.json():
                tokens.append({'contract': t.get('token_address'), 'balance': int(t.get('balance',0)), 'decimals': int(t.get('decimals',0)), 'symbol': t.get('symbol')})
    elif alchemy_key:
        url = f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}"
        payload = {'jsonrpc':'2.0','id':1,'method':'alchemy_getTokenBalances','params':[address, 'DEFAULT_TOKENS']}
        r = requests.post(url, json=payload, timeout=10).json()
        for tok in r.get('result', {}).get('tokenBalances', []):
            contract = tok.get('contractAddress')
            raw = int(tok.get('tokenBalance','0'), 16) if tok.get('tokenBalance') else 0
            tokens.append({'contract': contract, 'balance': raw})
    try:
        y = requests.get('https://api.yearn.fi/v1/chains/1/vaults/all', timeout=10).json()
        yearn_map = {v.get('address','').lower(): v for v in y if v.get('address')}
    except Exception:
        yearn_map = {}
    out = []
    for t in tokens:
        c = (t.get('contract') or '').lower()
        if c in yearn_map and t.get('balance',0) > 0:
            v = yearn_map[c]
            out.append({'contract': c, 'symbol': t.get('symbol'), 'balance': t.get('balance'), 'vault_name': v.get('display_name'), 'vault_address': c})
    return out

def claim_all_yearn_vaults(user_address, private_key, provider_project_id, dry_run=True, discord_webhook=None):
    if provider_project_id.startswith('http'):
        provider_url = provider_project_id
    else:
        provider_url = f'https://eth-mainnet.g.alchemy.com/v2/{provider_project_id}'
    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.isConnected():
        raise Exception('Provider not connected')
    claimable = list_vaults_for_address(user_address, alchemy_key=provider_project_id)
    plan = []
    nonce = w3.eth.get_transaction_count(user_address)
    for v in claimable:
        vault_addr = Web3.toChecksumAddress(v['vault_address'])
        contract = w3.eth.contract(address=vault_addr, abi=VAULT_ABI)
        try:
            shares = contract.functions.balanceOf(user_address).call()
        except Exception:
            shares = 0
        if shares == 0:
            continue
        tx = contract.functions.withdraw().build_transaction({'from': user_address, 'nonce': nonce})
        try:
            gas_est = w3.eth.estimate_gas(tx)
            gas_price = w3.eth.gas_price
        except Exception as e:
            gas_est = None
            gas_price = None
        plan.append({'vault': v['vault_name'], 'vault_address': v['vault_address'], 'shares': shares, 'nonce': nonce, 'gas_estimate': gas_est, 'gas_price': gas_price})
        nonce += 1
    if discord_webhook:
        msg = f"Dry-run plan for {user_address}: {len(plan)} tx(s)"
        extra = {'plan': json.dumps(plan)}
        try:
            log_discord(discord_webhook, 'Yearn Claim Dry-Run', msg, extra)
        except Exception:
            pass
    if dry_run:
        return {'dry_run': True, 'plan': plan}
    tx_hashes = []
    for p in plan:
        vault_addr = Web3.toChecksumAddress(p['vault_address'])
        contract = w3.eth.contract(address=vault_addr, abi=VAULT_ABI)
        tx = contract.functions.withdraw().build_transaction({'from': user_address, 'nonce': p['nonce'], 'gas': p.get('gas_estimate') or 400000, 'gasPrice': p.get('gas_price') or w3.eth.gas_price})
        signed = w3.eth.account.sign_transaction(tx, private_key)
        txh = w3.eth.send_raw_transaction(signed.rawTransaction)
        tx_hashes.append(w3.toHex(txh))
        time.sleep(6)
    if discord_webhook:
        try:
            log_discord(discord_webhook, 'Yearn Claim Executed', f'Executed {len(tx_hashes)} txs', {'tx_hashes': json.dumps(tx_hashes)})
        except Exception:
            pass
    return {'dry_run': False, 'tx_hashes': tx_hashes}
