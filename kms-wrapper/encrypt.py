import base64
import configparser
import json

from Crypto import Random
from Crypto.Cipher import AES
from aliyunsdkcore import client as alibaba_client
from aliyunsdkkms.request.v20160120 import GenerateDataKeyRequest

config = configparser.ConfigParser(allow_no_value=True)
config.read(".ini")
ACCESS_KEY_ID = config.get("USER_INFO", "access_key_id")
ACCESS_SECRET = config.get("USER_INFO", "access_secret")
REGION_ID = config.get("USER_INFO", "region_id")
KEY_ID = config.get("KEY_INFO", "key_id")


def aes_pad(sumstr):
    return sumstr + (32 - len(sumstr) % 32) * chr(32 - len(sumstr) % 32).encode()


def main():
    client = alibaba_client.AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, REGION_ID)

    gen_request = GenerateDataKeyRequest.GenerateDataKeyRequest()
    gen_request.set_KeyId(KEY_ID)
    gen_request.set_KeySpec("AES_128")
    gen_request.set_accept_format("json")
    gen_request.set_protocol_type("https")
    gen_response = client.do_action_with_exception(gen_request)

    datakeydict = json.loads(gen_response)
    datakey = base64.b64decode(datakeydict["Plaintext"])
    cipherdatakey = datakeydict["CiphertextBlob"]

    with open("./keys/ciphertext.txt", "w") as f:
        f.write(cipherdatakey)

    iv = Random.new().read(AES.block_size)
    cipher = AES.new(datakey, AES.MODE_CBC, iv)
    with open("testfiles/plaintext_password.txt") as f:
        raw_password = f.read()
        plaintext_password = aes_pad(raw_password.encode())
        print(f"Plain text password \n{raw_password}")
        ciphertext_password = base64.b64encode(
            iv + cipher.encrypt(plaintext_password)
        )
        with open("testfiles/cipher_password.txt", "w") as cp:
            cp.write(ciphertext_password.decode())
            print(f"Encrypted password \n{ciphertext_password.decode()}")


if __name__ == "__main__":
    exit(main())
