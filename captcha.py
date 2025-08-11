import requests, time

class TwoCaptchaClient:
    def __init__(self, api_key):
        self.key = api_key
    def submit_recaptcha(self, site_key, page_url):
        resp = requests.post('http://2captcha.com/in.php', data={
            'key': self.key, 'method': 'userrecaptcha', 'googlekey': site_key, 'pageurl': page_url, 'json':1
        }, timeout=10).json()
        if resp.get('status') != 1:
            raise Exception('submit error: ' + str(resp))
        return resp.get('request')
    def fetch_solution(self, req_id, timeout=120, interval=5):
        url = 'http://2captcha.com/res.php'
        start = time.time()
        while time.time() - start < timeout:
            r = requests.get(url, params={'key': self.key, 'action':'get', 'id': req_id, 'json':1}, timeout=10).json()
            if r.get('status') == 1:
                return r.get('request')
            time.sleep(interval)
        raise TimeoutError('No solution')

class AntiCaptchaClient:
    def __init__(self, api_key):
        self.key = api_key
    def create_task(self, task_payload):
        url = 'https://api.anti-captcha.com/createTask'
        headers = {'Content-Type':'application/json'}
        data = {'clientKey': self.key, 'task': task_payload}
        r = requests.post(url, json=data, headers=headers, timeout=10).json()
        return r
    def get_result(self, task_id):
        url = 'https://api.anti-captcha.com/getTaskResult'
        data = {'clientKey': self.key, 'taskId': task_id}
        r = requests.post(url, json=data, timeout=10).json()
        return r
