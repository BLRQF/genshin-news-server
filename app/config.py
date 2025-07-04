import yaml

with open("./app/api_config.yml", encoding="utf-8") as f:
    API_CONFIG = yaml.safe_load(f)

SUPPORTED_PARAMS = ['genshin.web_cn']
CACHE_TIME = 5 * 60
CACHE_INVALID_TIME = 2 * 24 * 3600
CACHE_PATH = "./data"
VIDEO_PATTERN = r"https?://[^ ]+\.(mp4|mov)"