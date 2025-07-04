from importlib import import_module
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.tools import read_cache, write_cache, is_expired

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
)

@app.on_event('startup')
async def startup_event():
    print('SUPPORTED_PARAMS', config.SUPPORTED_PARAMS)
    for params in config.SUPPORTED_PARAMS:
        cache = read_cache(params)
        if cache is None or is_expired(cache['update'], config.CACHE_INVALID_TIME):
            print(f'未检测到 {params} 缓存或缓存已过期')

@app.get('/{game}/{channel}')
async def get_game_news(game: str, channel: str, force_refresh: int = 0):
    index = f'{game}.{channel}'
    if index not in config.SUPPORTED_PARAMS:
        return {'code': 1, 'msg': '配置不存在'}

    channel_config = config.API_CONFIG[game][channel]

    cache = read_cache(index)
    if cache is not None and force_refresh == 0:
        if not is_expired(cache['update'], config.CACHE_TIME):
            return {'code': 0, **cache}
        
    try:
        adapter = import_module(f'app.adapter.{channel_config["adapter"]}')
        data = adapter.get_news(channel_config, cache=cache)
        if data is None:
            if cache:
                return {'code': 1, 'msg': '刷新数据失败，请稍后再试，如有疑问请在 Github Issue 中提出', **cache}
            return {'code': 1, 'msg': '刷新数据失败，请稍后再试，如有疑问请在 Github Issue 中提出'}

        write_cache(index, data)
        return {'code': 0, **data}
    except Exception as e:
        print(e)
        if cache:
            return {'code': 1, 'msg': '服务器错误，请稍后再试，如有疑问请在 Github Issue 中提出', **cache}
        return {'code': 1, 'msg': '服务器错误，请稍后再试，如有疑问请在 Github Issue 中提出'}