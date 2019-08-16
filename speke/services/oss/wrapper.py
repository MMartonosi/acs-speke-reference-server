import io

import oss2

from config import ACCESS_KEY_ID, ACCESS_SECRET, OSS_BUCKET_NAME, OSS_ENDPOINT

auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_SECRET)
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)


def acs_oss_create_secret(content_id, secret):
    text_stream = io.BytesIO(secret)
    # Store secret of a content in a folder/secret-like struture
    bucket.put_object(f"{content_id}/secret.txt", text_stream.read())


def acs_oss_get_secret(content_id):
    cipher_text = bucket.get_object(f"{content_id}/secret.txt")
    return cipher_text.read()
