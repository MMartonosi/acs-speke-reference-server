import base64
import json

from aliyunsdkkms.request.v20160120 import GenerateDataKeyRequest

from config.config import get_acs_client, get_key_id


def generic_acs_generate_data_key_request():
    gen_request = GenerateDataKeyRequest.GenerateDataKeyRequest()
    gen_request.set_KeyId(get_key_id())
    gen_request.set_KeySpec("AES_128")
    gen_request.set_accept_format("json")
    gen_request.set_protocol_type("https")
    gen_response = get_acs_client().do_action_with_exception(gen_request)
    data_key_dict = json.loads(gen_response)
    data_key = base64.b64decode(data_key_dict["Plaintext"])
    cipher_key = data_key_dict["CiphertextBlob"]
    return data_key, cipher_key
