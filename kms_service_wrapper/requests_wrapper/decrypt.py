import base64
import json
from aliyunsdkkms.request.v20160120 import DecryptRequest
from config.config import get_acs_client


def generic_acs_decrypt_request(cipher_key):
    decrypt_request = DecryptRequest.DecryptRequest()
    decrypt_request.set_CiphertextBlob(cipher_key)
    decrypt_request.set_accept_format("json")
    decrypt_request.set_protocol_type("https")
    decrypt_response = get_acs_client.do_action_with_exception(decrypt_request)
    plain_text_dict = json.loads(decrypt_response)
    data_key = base64.b64decode(plain_text_dict["Plaintext"])
    return data_key
