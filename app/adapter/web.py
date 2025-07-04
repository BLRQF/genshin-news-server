import requests
import json, re, math
from typing import Any, Dict, List, Optional
from requests.adapters import HTTPAdapter

from app import config
from app.tools import get_time

PAGE_SIZE = 100

def extraction_news(raw_news: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        'id': raw_news.get('iInfoId'),
        'title': raw_news.get('sTitle'),
        'startTime': raw_news.get('dtStartTime'),
        'createTime': raw_news.get('dtCreateTime'),
        'cover': None,
        'video': None,
    }
    try:
        ext_data = json.loads(raw_news.get('sExt', '{}'))
    except json.JSONDecodeError:
        ext_data = {}
    for ext in ext_data:
        ext_list = ext_data[ext]
        if not isinstance(ext_list, list):
            continue
        for data in ext_list:
            url = data.get('url')
            if url and url.startswith('http'):
                result['cover'] = url
                break
        if result['cover']:
            break
    if video := re.search(config.VIDEO_PATTERN, raw_news.get('sContent', '')):
        result['video'] = video.group(0)
    return result

def get_count(api_url: str):
    res = requests.get(api_url.format(page=1, page_size=5), timeout=5)
    if res.status_code != 200:
        return None
    ret_data = res.json()
    if ret_data.get('retcode') != 0:
        return None
    return ret_data.get('data', {}).get('iTotal')

def combine_news(cache_news, new_news, total):
    if total <= len(new_news):
        return new_news
    return new_news + cache_news[-(total - len(new_news)):]

def get_page(session: requests.Session, api_url: str, page_size: int, page: int) -> List[Dict[str, Any]]:
    res = session.get(api_url.format(page_size=page_size, page=page), timeout=5)
    if res.status_code != 200:
        return []
    ret_data = res.json()
    if ret_data.get('retcode') != 0:
        return []
    return ret_data.get('data', {}).get('list', [])

def get_news(config: Dict[str, Any], cache: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    api_url = config['url']

    news_list: List[Dict[str, Any]] = []
    news_count = get_count(api_url)
    if news_count is None:
        return None

    cache_data = cache.get('data', []) if cache else []
    print(f'Count:{news_count}, Cache: {len(cache_data)}')
    current_page = 1
    max_page = math.ceil((news_count - len(cache_data)) / PAGE_SIZE)
    if max_page <= 0:
        max_page = 1
    print(f'Max Page: {max_page}')

    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=3))
    try:
        while current_page <= max_page:
            print(f'get page {current_page}')
            page_data = get_page(session, api_url, PAGE_SIZE, current_page)
            news_list.extend(page_data)
            current_page += 1
    finally:
        session.close()

    new_news = [extraction_news(news) for news in news_list]
    news_list = combine_news(cache_data, new_news, news_count)

    return {
        'data': news_list,
        'update': get_time()
    }