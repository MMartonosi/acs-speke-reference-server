import os

# import boto3
# from botocore.exceptions import ClientError
from oss2.exceptions import NoSuchKey

from services.oss import acs_oss_get_secret, acs_oss_create_secret


# import secrets


class KeyGenerator:
    """
    This class is responsible for symmetric key generation. Different
    functions are provided to generate keys. This class also manages the
    secret data used by each content ID in key generation.
    """

    def __init__(self):
        self.local_secret_directory = "/tmp/.speke/secrets"
        if not os.path.exists(self.local_secret_directory):
            os.makedirs(self.local_secret_directory)

    def local_secret_path(self, content_id):
        """
        Create a path for a content ID secret file stored locally in the Lambda filesystem
        """
        return f"{self.local_secret_directory}/{content_id}"

    def store_local_secret(self, content_id, secret):
        """
        Store a content ID secret file
        """
        secret_file = self.local_secret_path(content_id)
        secret_file = open(secret_file, 'w')
        secret_file.write(secret)
        secret_file.close()

    def retrieve_local_secret(self, content_id):
        """
        Retrieve a content ID secret file
        """
        secret_file = self.local_secret_path(content_id)
        secret_file = open(secret_file, 'r')
        secret = secret_file.read()
        secret_file.close()
        return secret

    def retrieve_content_id_secret(self, content_id):
        """
        Retrieve the secret value by content ID used for generating keys
        """
        from speke.key_server import app

        try:
            # cached locally?
            secret = self.retrieve_local_secret(content_id)
            app.logger.info(f"Retrieved secret from cache for: {content_id}")
        except (IOError, FileNotFoundError):
            # try oss
            try:
                secret = acs_oss_get_secret(content_id)
                self.store_local_secret(content_id, secret)
                app.logger.info(f"Retrieved secret from oss storage for: {content_id}")
            except NoSuchKey:
                # create new content and salt for it
                # new secret value
                # TODO: move this to config of the class
                content_id_secret_length = 64
                # generate random string "password"
                secret = self.generate_password(content_id_secret_length)

                # store on oss and in local cache
                acs_oss_create_secret(content_id, secret)

                self.store_local_secret(content_id, secret)
                app.logger.info(f"Created secret for: {content_id}")
        return secret

    def key(self, content_id, key_id):
        """
        Return a symmetric key based on a content ID and key ID
        """
        # TODO: fix late imports
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.backends import default_backend

        # Setup for key derivation function (default)
        backend = default_backend()
        derived_key_iterations = 5000
        derived_key_size = 16
        # Generate a key using a key derivation function (default)

        salt = self.retrieve_content_id_secret(content_id)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=derived_key_size,
                         salt=salt.encode(),
                         iterations=derived_key_iterations,
                         backend=backend)
        return kdf.derive(key_id.encode())

    def generate_password(self, length):
        # https://docs.python.org/3/library/secrets.html#recipes-and-best-practices
        import secrets  # TODO: FIX LATE IMPORT
        import string  # TODO: FIX LATE IMPORT
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(length))
