import os
import secrets
import string

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from oss2.exceptions import NoSuchKey

from speke.services.oss import acs_oss_create_secret, acs_oss_get_secret


def get_app():
    from speke.key_server import app
    return app


class KeyGenerator:
    def __init__(self):
        self.local_secret_directory = "/tmp/.speke/secrets"
        self.content_id_secret_length = 64
        if not os.path.exists(self.local_secret_directory):
            os.makedirs(self.local_secret_directory)

    def local_secret_path(self, content_id):
        return f"{self.local_secret_directory}/{content_id}"

    def store_local_secret(self, content_id, secret):
        secret_file = self.local_secret_path(content_id)
        secret_file = open(secret_file, "w")
        secret_file.write(secret)
        secret_file.close()

    def retrieve_local_secret(self, content_id):
        secret_file = self.local_secret_path(content_id)
        secret_file = open(secret_file, "r")
        secret = secret_file.read()
        secret_file.close()
        return secret

    def retrieve_content_id_secret(self, content_id):
        app = get_app()

        try:
            secret = self.retrieve_local_secret(content_id)
            app.logger.info(f"Retrieved secret from cache for: {content_id}")
        except (IOError, FileNotFoundError):
            try:
                secret = acs_oss_get_secret(content_id)
                self.store_local_secret(content_id, secret)
                app.logger.info(f"Retrieved secret from oss storage for: {content_id}")
            except NoSuchKey:
                secret = self.generate_password(self.content_id_secret_length)
                acs_oss_create_secret(content_id, secret)
                self.store_local_secret(content_id, secret)
                app.logger.info(f"Created secret for: {content_id}")
        return secret

    def key(self, content_id, key_id):
        backend = default_backend()
        derived_key_iterations = 5000
        derived_key_size = 16
        salt = self.retrieve_content_id_secret(content_id)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=derived_key_size,
            salt=salt.encode(),
            iterations=derived_key_iterations,
            backend=backend,
        )
        return kdf.derive(key_id.encode())

    def generate_password(self, length):
        # https://docs.python.org/3/library/secrets.html#recipes-and-best-practices
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(length))
