import json, os, time
TEMPLATES_FILE = 'survey_templates.json'
QUEUE_FILE = 'survey_queue.json'

def save_template(name, answers):
    templates = {}
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE,'r') as f:
            templates = json.load(f)
    templates[name] = answers
    with open(TEMPLATES_FILE,'w') as f:
        json.dump(templates, f)

def list_templates():
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE,'r') as f:
            return json.load(f)
    return {}

def enqueue_survey(url, template_name):
    q = []
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE,'r') as f:
            q = json.load(f)
    q.append({'url':url, 'template': template_name, 'ts': int(time.time())})
    with open(QUEUE_FILE,'w') as f:
        json.dump(q, f)
    return True

def list_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE,'r') as f:
            return json.load(f)
    return []
