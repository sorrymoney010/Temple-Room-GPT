import requests, time, json

def get_channel_balance(channel_name, lbry_rpc_url=None):
    try:
        if lbry_rpc_url:
            payload = {"jsonrpc":"2.0","method":"wallet_balance","params":[],"id":1}
            r = requests.post(lbry_rpc_url, json=payload, timeout=10).json()
            return {'source':'lbry_rpc','result': r}
        resp = requests.get(f'https://api.odysee.com/api/v1/user?name={channel_name}', timeout=10)
        return resp.json()
    except Exception as e:
        return {'error': str(e)}
