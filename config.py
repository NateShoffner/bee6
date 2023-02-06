import json

CONFIG_NAME = 'config/config.json'

def load_config() -> dict:
    with open(CONFIG_NAME) as f:
        c = json.load(f)
    return c

def save_config(c: dict):
    with open(CONFIG_NAME, 'w') as f:
        json.dump(c, f, indent=4)