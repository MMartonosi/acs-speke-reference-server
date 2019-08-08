import base64
import configparser
import json

from Crypto.Cipher import AES
from aliyunsdkcore import client as alibaba_client
from aliyunsdkkms.request.v20160120 import DecryptRequest

config = configparser.ConfigParser(allow_no_value=True)
config.read(".ini")
ACCESS_KEY_ID = config.get("USER_INFO", "access_key_id")
ACCESS_SECRET = config.get("USER_INFO", "access_secret")
REGION_ID = config.get("USER_INFO", "region_id")
KEY_ID = config.get("KEY_INFO", "key_id")


def aes256unpad(s):
    return s[:-ord(s[len(s) - 1:])]


def main():
    client = alibaba_client.AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, REGION_ID)
    with open("keys/ciphertext.txt") as f:
        cipher_data_key = f.read()

        decrypt_request = DecryptRequest.DecryptRequest()
        decrypt_request.set_CiphertextBlob(cipher_data_key)
        decrypt_request.set_accept_format("json")
        decrypt_request.set_protocol_type("https")
        decrypt_response = client.do_action_with_exception(decrypt_request)

        plaintextdict = json.loads(decrypt_response)
        datakey = base64.b64decode(plaintextdict["Plaintext"])

        with open("testfiles/cipher_password.txt") as cp:
            cipher_content = cp.read()
            cipher = base64.b64decode(cipher_content)
            iv = cipher[:AES.block_size]
            aes = AES.new(datakey, AES.MODE_CBC, iv)
            decrypted = aes.decrypt(cipher[AES.block_size:]).decode()
            print(decrypted)


if __name__ == "__main__":
    exit(main())
