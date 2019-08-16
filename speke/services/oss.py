import io

import oss2
import os

auth = oss2.Auth(os.environ["ACCESS_KEY_ID"], os.environ["ACCESS_SECRET"])
bucket = oss2.Bucket(auth, os.environ["OSS_ENDPOINT"], os.environ["OSS_BUCKET_NAME"])

def acs_oss_create_secret(content_id, secret):
    text_stream = io.BytesIO(secret)
    # Store secret of a content in a folder/secret-like struture
    bucket.put_object(f"{content_id}/secret.txt", text_stream.read())


def acs_oss_get_secret(content_id):
    cipher_text = bucket.get_object(f"{content_id}/secret.txt")
    return cipher_text.read()
