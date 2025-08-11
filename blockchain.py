import requests
from web3 import Web3

def get_eth_balance(address):
    if not address:
        return None
    try:
        from streamlit import secrets as _s
        alchemy = _s["blockchain"].get("alchemy_key")
    except Exception:
        alchemy = None
    if not alchemy:
        return None
    url = f"https://eth-mainnet.g.alchemy.com/v2/{alchemy}"
    payload = {"jsonrpc":"2.0","id":1,"method":"eth_getBalance","params":[address, 'latest']}
    r = requests.post(url, json=payload, timeout=10).json()
    wei = int(r.get('result','0'), 16)
    return wei / 1e18
