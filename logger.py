import requests, time

def log_discord(webhook_url, title, message, extra=None):
    if not webhook_url:
        return False
    payload = {
        "username": "KarmicBotFarm-Logger",
        "embeds": [
            {
                "title": title,
                "description": message,
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        ]
    }
    if extra:
        try:
            payload['embeds'][0]['fields'] = [{'name':k, 'value':str(v), 'inline':False} for k,v in extra.items()]
        except Exception:
            pass
    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        return r.status_code in (200,204)
    except Exception:
        return False
