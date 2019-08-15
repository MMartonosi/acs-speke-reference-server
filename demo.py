import base64
import os
import sys

from Crypto import Random
from Crypto.Cipher import AES

# import config
sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "config"))
)


from kms.wrapper import acs_kms_generate_data_key, acs_kms_decrypt_cipher_key

from oss.wrapper import acs_oss_create_secret, acs_oss_get_secret

RHB_UUIDs = [
    "948e65c0-55b6-4ca3-9d5c-feb8e3dc2a3a",
    "28c94cfa-8433-47d5-a6fe-48f22a3f074e",
    "70668ace-dcfa-4d1d-815b-fe83eeb0e34c",
]


def aes_pad(sumstr):
    return sumstr + (32 - len(sumstr) % 32) * chr(32 - len(sumstr) % 32).encode()


def main():
    operation = sys.argv[1]
    if operation == "encrypt":
        text_to_encrypt = sys.argv[2]
        data_key, cipher_key = acs_kms_generate_data_key()
        acs_oss_create_secret(RHB_UUIDs[0], cipher_key)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(data_key, AES.MODE_CBC, iv)
        plaintext_password = aes_pad(text_to_encrypt.encode())
        print(f"Plain text password \n{text_to_encrypt}")
        ciphertext_password = base64.b64encode(iv + cipher.encrypt(plaintext_password))
        print(f"Encrypted password \n{ciphertext_password.decode()}")
    elif operation == "decrypt":
        text_to_decrypt = sys.argv[2]
        cipher_key = acs_oss_get_secret(RHB_UUIDs[0])
        data_key = acs_kms_decrypt_cipher_key(cipher_key)
        cipher = base64.b64decode(text_to_decrypt)
        iv = cipher[: AES.block_size]
        aes = AES.new(data_key, AES.MODE_CBC, iv)
        decrypted = aes.decrypt(cipher[AES.block_size :]).decode()
        print(decrypted)
    else:
        print("execute with eg 'python demo.py [encrypt/decrypt]'")
        return 1


if __name__ == "__main__":
    exit(main())
