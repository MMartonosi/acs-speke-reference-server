import base64

from Crypto import Random
from Crypto.Cipher import AES
from kms_service_wrapper.requests_wrapper.generate_data_key import (
    generic_acs_generate_data_key_request,
)


def aes_pad(sumstr):
    return sumstr + (32 - len(sumstr) % 32) * chr(32 - len(sumstr) % 32).encode()


def main():
    data_key, cipher_key = generic_acs_generate_data_key_request()

    with open("./keys/ciphertext.txt", "w") as f:
        f.write(cipher_key)

    iv = Random.new().read(AES.block_size)
    cipher = AES.new(data_key, AES.MODE_CBC, iv)
    with open("testfiles/plaintext_password.txt") as f:
        raw_password = f.read()
        plaintext_password = aes_pad(raw_password.encode())
        print(f"Plain text password \n{raw_password}")
        ciphertext_password = base64.b64encode(iv + cipher.encrypt(plaintext_password))
        with open("testfiles/cipher_password.txt", "w") as cp:
            cp.write(ciphertext_password.decode())
            print(f"Encrypted password \n{ciphertext_password.decode()}")


if __name__ == "__main__":
    exit(main())
