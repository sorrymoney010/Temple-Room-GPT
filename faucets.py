import requests, time, json
from utils.logger import log_discord

def claim_freebitco_in(cookie, dry_run=True, discord_webhook=None):
    if not cookie:
        return {'error': 'no cookie provided'}
    headers = {'Cookie': cookie, 'User-Agent': 'karmic-bot/1.0'}
    try:
        r = requests.get('https://freebitco.in/', headers=headers, timeout=15)
        if r.status_code != 200:
            return {'error': 'site returned non-200'}
        result = {'status': 'checked_homepage', 'code': r.status_code}
    except Exception as e:
        return {'error': str(e)}
    if dry_run:
        if discord_webhook:
            log_discord(discord_webhook, 'Faucet Dry-Run', 'FreeBitco.in check performed', {'status': result})
        return {'dry_run': True, 'result': result}
    if discord_webhook:
        log_discord(discord_webhook, 'Faucet Claim Attempt', 'Attempted non-dry faucet claim (placeholder)', {'status': result})
    return {'error': 'Auto-claim for FreeBitco.in not implemented - requires headless browser and captcha handling'}

def claim_cointiply(api_key, dry_run=True, discord_webhook=None):
    if not api_key:
        return {'error': 'no api key'}
    try:
        r = requests.get(f'https://cointiply.com/api/v1/user?api_key={api_key}', timeout=15)
        result = {'status_code': r.status_code, 'response': r.text[:200]}
    except Exception as e:
        return {'error': str(e)}
    if dry_run:
        if discord_webhook:
            log_discord(discord_webhook, 'Faucet Dry-Run', 'Cointiply API check performed', {'status': result})
        return {'dry_run': True, 'result': result}
    return {'error': 'Auto-claim not implemented for Cointiply; implement per their API docs'}

def run_all_claims(faucet_secrets, wallet_secrets, dry_run=True, discord_webhook=None):
    res = {}
    res['freebitco'] = claim_freebitco_in(faucet_secrets.get('freebitco_cookie'), dry_run=dry_run, discord_webhook=discord_webhook)
    res['cointiply'] = claim_cointiply(faucet_secrets.get('cointiply_api_key') or faucet_secrets.get('cointiply_api_key'), dry_run=dry_run, discord_webhook=discord_webhook)
    if discord_webhook:
        log_discord(discord_webhook, 'Faucet Run', 'Completed faucet run (dry_run=%s)' % str(dry_run), {'results': json.dumps(res)})
    return res
