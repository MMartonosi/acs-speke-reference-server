import configparser

import os

CONFIG_ROOT = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))

LOADED: bool = False
ACCESS_KEY_ID: str = ""
ACCESS_SECRET: str = ""
REGION_ID: str = ""
# KEY_ID: str = ""
OSS_ENDPOINT: str = ""
OSS_BUCKET_NAME: str = ""


def init():
    global ACCESS_KEY_ID, ACCESS_SECRET, REGION_ID, KEY_ID, OSS_ENDPOINT, OSS_BUCKET_NAME, LOADED
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(CONFIG_ROOT, ".ini")))
    ACCESS_KEY_ID = config.get("RAM", "access_key_id")
    ACCESS_SECRET = config.get("RAM", "access_secret")
    REGION_ID = config.get("RAM", "region_id")
    # KEY_ID = config.get("KMS", "cmk_id")
    OSS_ENDPOINT = config.get("OSS", "endpoint")
    OSS_BUCKET_NAME = config.get("OSS", "bucket_name")
    LOADED = True


if not LOADED:
    init()
