import base64

from Crypto.Cipher import AES

from kms_service_wrapper.requests_wrapper.decrypt import generic_acs_decrypt_request


def main():
    with open("keys/ciphertext.txt") as f:
        cipher_key = f.read()
        data_key = generic_acs_decrypt_request(cipher_key)

        with open("testfiles/cipher_password.txt") as cp:
            cipher_content = cp.read()
            cipher = base64.b64decode(cipher_content)
            iv = cipher[: AES.block_size]
            aes = AES.new(data_key, AES.MODE_CBC, iv)
            decrypted = aes.decrypt(cipher[AES.block_size :]).decode()
            print(decrypted)


if __name__ == "__main__":
    exit(main())
