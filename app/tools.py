import json, os
from datetime import datetime

from app import config

def get_time() -> int:
    return int(datetime.now().timestamp())

def is_expired(cache_timestamp: int, duration: int) -> bool:
    if cache_timestamp is None:
        return True
    return cache_timestamp + duration < get_time()

def read_cache(cache_name: str) -> dict | None:
    filename = os.path.join(config.CACHE_PATH, f'{cache_name}.json')
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return None

def write_cache(cache_name: str, data: dict):
    if not os.path.exists(config.CACHE_PATH):
        os.makedirs(config.CACHE_PATH)
    filename = os.path.join(config.CACHE_PATH, f'{cache_name}.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)