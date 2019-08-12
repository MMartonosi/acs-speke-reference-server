import configparser

from aliyunsdkcore import client
import os

CONFIG_ROOT = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))

COUNTER: int = 0
LOADED: int = 0
ACCESS_KEY_ID: str = ""
ACCESS_SECRET: str = ""
REGION_ID: str = ""
KEY_ID: str = ""
OSS_ENDPOINT: str = ""
OSS_BUCKET_NAME: str = ""


def get_config():
    global COUNTER
    COUNTER += 1

    global ACCESS_KEY_ID, ACCESS_SECRET, REGION_ID, KEY_ID, OSS_ENDPOINT, OSS_BUCKET_NAME, LOADED
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(CONFIG_ROOT, ".ini")))
    ACCESS_KEY_ID = config.get("RAM", "access_key_id")
    ACCESS_SECRET = config.get("RAM", "access_secret")
    REGION_ID = config.get("RAM", "region_id")
    KEY_ID = config.get("KMS", "cmk_id")
    OSS_ENDPOINT = config.get("OSS", "endpoint")
    OSS_BUCKET_NAME = config.get("OSS", "bucket_name")
    LOADED = 1


if LOADED == 0:
    get_config()

# def get_acs_client():
#     access_key_id, access_secret, region_id, key_id = get_config()
#     return client.AcsClient(access_key_id, access_secret, region_id)
#
#
# def get_access_secret():
#     access_key_id, access_secret, region_id, key_id = get_config()
#     return access_secret, access_secret
#
#
# def get_key_id():
#     access_key_id, access_secret, region_id, key_id = get_config()
#     return key_id
