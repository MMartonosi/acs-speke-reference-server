import hashlib

# import secrets

# import boto3
# from botocore.exceptions import ClientError

from oss2.exceptions import ClientError


class KeyGenerator:
    """
    This class is responsible for symmetric key generation. Different
    functions are provided to generate keys. This class also manages the
    secret data used by each content ID in key generation.
    """

    def __init__(self):
        # TODO: change into alibaba cloud local storage dir
        self.local_secret_folder = "/home/alibaba_speke_testing/"

        # self.secrets_client = boto3.client('secretsmanager')


    # Related to caching
    # def local_secret_path(self, content_id):
    #     """
    #     Create a path for a content ID secret file stored locally in the Lambda filesystem
    #     """
    #     return f"{self.local_secret_folder}/speke.{content_id}"

    # Related to caching
    # def store_local_secret(self, content_id, secret):
    #     """
    #     Store a content ID secret file
    #     """
    #     secret_file = self.local_secret_path(content_id)
    #     secret_file = open(secret_file, 'w')
    #     secret_file.write(secret)
    #     secret_file.close()

    # Related to acching
    # def retrieve_local_secret(self, content_id):
    #     """
    #     Retrieve a content ID secret file
    #     """
    #     secret_file = self.local_secret_path(content_id)
    #     secret_file = open(secret_file, 'r')
    #     secret = secret_file.read()
    #     secret_file.close()
    #     return secret

    def retrieve_content_id_secret(self, content_id):
        """
        Retrieve the secret value by content ID used for generating keys
        """

        from services.oss.wrapper import \
            acs_oss_get_secret  # TODO: fix this late import

        # TODO: implement caching
        print("SECRET FROM OSS")
        secret = acs_oss_get_secret(content_id)
        # try:
        #     # cached locally?
        #     secret = self.retrieve_local_secret(content_id)
        #     print("GOT SECRET FROM CACHE")
        #     print(f"SECRET: {content_id}")
        # except IOError:
        #     # try secrets manager (oss in alibaba case)
        #     # secret_id = f"speke/{content_id}"
        #     try:
        #         # response = self.secrets_client.get_secret_value(SecretId=secret_id)
        #         secret = acs_oss_get_secret(content_id)
        #     # oos get key by secret_id(path - id of rhb)
        #     # secret = response['SecretString']
        #     # self.store_local_secret(content_id, secret)
        #     # oss.store_secret()
        #         print("GOT SECRET FROM SECRETS MANAGER")
        #         print(f"SECRET: {content_id}")
        #     except ClientError as error:
        #         if error.response['Error']['Code'] == 'ResourceNotFoundException':
        #             # new secret value
        #             content_id_secret_length = 64
        #             secret = self.secrets_client.get_random_password(
        #                          PasswordLength=content_id_secret_length)['RandomPassword']
        #         # we need a new secret value
        #
        #         # set length
        #         content_id_secret_length = 64
        #
        #         print("CREATE-SECRET {}".format(content_id))
        #         secret = self.secrets_client.get_random_password(
        #             PasswordLength=content_id_secret_length)['RandomPassword']
        #         self.secrets_client.create_secret(Name=secret_id,
        #                                           SecretString=secret,
        #                                           Description='SPEKE content ID secret value for key generation')
        #         self.store_local_secret(content_id, secret)
        #     else:
        #         # we're done trying
        #         raise error
        return secret

    def key(self, content_id, key_id):
        """
        Return a symmetric key based on a content ID and key ID
        """
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
                         salt=salt,
                         iterations=derived_key_iterations,
                         backend=backend)
        return kdf.derive(key_id.encode('utf-8'))
