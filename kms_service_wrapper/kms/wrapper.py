import base64
import sys

from aliyunsdkkms.request.v20160120 import GenerateDataKeyRequest

from config import KEY_ID

sys.path.append("../../")
import json
from aliyunsdkkms.request.v20160120 import DecryptRequest
from aliyunsdkcore.client import AcsClient

from config import ACCESS_KEY_ID, ACCESS_SECRET, REGION_ID


def acs_kms_generate_data_key():
    client = AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, REGION_ID)
    gen_request = GenerateDataKeyRequest.GenerateDataKeyRequest()
    gen_request.set_KeyId(KEY_ID)
    gen_request.set_KeySpec("AES_128")
    gen_request.set_accept_format("json")
    gen_request.set_protocol_type("https")
    gen_response = client.do_action_with_exception(gen_request)
    data_key_dict = json.loads(gen_response)
    data_key = base64.b64decode(data_key_dict["Plaintext"])
    cipher_key = data_key_dict["CiphertextBlob"]
    return data_key, cipher_key


def acs_kms_decrypt_cipher_key(cipher_key):
    client = AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, REGION_ID)
    decrypt_request = DecryptRequest.DecryptRequest()
    decrypt_request.set_CiphertextBlob(cipher_key)
    decrypt_request.set_accept_format("json")
    decrypt_request.set_protocol_type("https")
    decrypt_response = client.do_action_with_exception(decrypt_request)
    plain_text_dict = json.loads(decrypt_response)
    data_key = base64.b64decode(plain_text_dict["Plaintext"])
    return data_key
