import streamlit as st
from bots import yearn_claim, faucets, odysee, captcha, surveys, blockchain
import time

st.set_page_config(page_title="Karmic Bot Farm - Complete", layout="wide")
st.title("🧿 Karmic Bot Farm — Complete Earning Suite")

settings = st.secrets.get('settings', {})
enable_auto = settings.get('enable_auto_claim', False)
enable_faucet_auto = settings.get('enable_faucet_auto_claim', False)
dry_run = settings.get('dry_run_mode', True)

st.sidebar.header("Settings")
st.sidebar.write(f"Auto-claim enabled: {enable_auto} (set in secrets)")
st.sidebar.write(f"Faucet auto-claim enabled: {enable_faucet_auto} (set in secrets)")
st.sidebar.write(f"Dry-run mode: {dry_run} (set in secrets)")

eth_addr = st.secrets.get("wallets", {}).get("eth_address", "")
channel = st.secrets.get('odysee', {}).get('channel_name', '')
webhook = st.secrets.get('logging', {}).get('discord_webhook')

st.sidebar.write(f"Monitored ETH: {eth_addr}")

if st.button("Refresh Balances"):
    st.session_state['last_refresh'] = time.time()

st.subheader('Balances & Blockchain')
eth_bal = blockchain.get_eth_balance(eth_addr)
st.metric('ETH Balance', eth_bal if eth_bal is not None else 'error')

st.subheader('Yearn Vaults')
if st.button('List claimable Yearn vaults'):
    try:
        vaults = yearn_claim.list_vaults_for_address(eth_addr, alchemy_key=st.secrets.get('blockchain',{}).get('alchemy_key'))
        st.table(vaults)
    except Exception as e:
        st.error(f'Error listing vaults: {e}')

if st.button('Estimate Yearn claim (dry-run)'):
    try:
        provider = st.secrets.get('blockchain',{}).get('alchemy_key') or st.secrets.get('blockchain',{}).get('infura_project_id')
        plan = yearn_claim.claim_all_yearn_vaults(eth_addr, None, provider, dry_run=True, discord_webhook=webhook)
        st.json(plan)
    except Exception as e:
        st.error(f'Estimate error: {e}')

if st.button('Claim Yearn earnings (execute)'):
    if not enable_auto:
        st.error('Auto-claim is disabled in secrets. To enable set settings.enable_auto_claim = true')
    else:
        pk = st.secrets.get('wallets', {}).get('private_key')
        provider = st.secrets.get('blockchain', {}).get('alchemy_key') or st.secrets.get('blockchain', {}).get('infura_project_id')
        if not pk or not provider:
            st.error('Missing private_key or provider in secrets. Add them before claiming.')
        else:
            with st.spinner('Claiming...'):
                try:
                    txs = yearn_claim.claim_all_yearn_vaults(eth_addr, pk, provider, dry_run=False, discord_webhook=webhook)
                    st.success('Claim transactions submitted:')
                    st.write(txs)
                except Exception as e:
                    st.error(f'Claim error: {e}')

st.subheader('Odysee')
if st.button('Check Odysee channel balance'):
    try:
        res = odysee.get_channel_balance(channel, lbry_rpc_url=st.secrets.get('odysee',{}).get('lbry_rpc_url'))
        st.json(res)
    except Exception as e:
        st.error(f'Odysee error: {e}')

st.subheader('Captcha Solver (2Captcha / Anti-Captcha)')
site_key = st.text_input('reCAPTCHA site-key (for testing)')
page_url = st.text_input('page URL for test')
if st.button('Submit captcha test to 2Captcha'):
    key = st.secrets.get('captcha',{}).get('twocaptcha_key')
    if not key:
        st.error('Add twocaptcha_key to secrets')
    else:
        try:
            client = captcha.TwoCaptchaClient(key)
            req_id = client.submit_recaptcha(site_key, page_url)
            sol = client.fetch_solution(req_id)
            st.success('Solution fetched: (paste into form)')
            st.code(sol)
        except Exception as e:
            st.error(f'Captcha error: {e}')

st.subheader('Surveys helper')
if st.button('List survey templates'):
    st.json(surveys.list_templates())

if st.button('List queued surveys'):
    st.json(surveys.list_queue())

st.subheader('Faucets')
if st.button('Estimate Faucets (dry-run)'):
    try:
        res = faucets.run_all_claims(st.secrets.get('faucets', {}), st.secrets.get('wallets', {}), dry_run=True, discord_webhook=webhook)
        st.json(res)
    except Exception as e:
        st.error(f'Estimate error: {e}')

if st.button('Run faucet auto-claim now (execute)'):
    if not enable_faucet_auto:
        st.error('Faucet auto-claim disabled. Enable in secrets (settings.enable_faucet_auto_claim = true)')
    else:
        try:
            res = faucets.run_all_claims(st.secrets.get('faucets', {}), st.secrets.get('wallets', {}), dry_run=False, discord_webhook=webhook)
            st.write(res)
        except Exception as e:
            st.error(f'Faucet error: {e}')

st.write('---')
st.caption('Security: Auto-claim features require a private key and will broadcast on-chain transactions. Use withdrawal-only keys and test carefully on small amounts.')
