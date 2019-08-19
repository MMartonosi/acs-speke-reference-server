import io
import os

import oss2

auth = oss2.Auth(os.environ["ACCESS_KEY_ID"], os.environ["ACCESS_SECRET"])
bucket = oss2.Bucket(auth, os.environ["OSS_ENDPOINT"], os.environ["OSS_BUCKET_NAME"])


def acs_oss_create_secret(content_id, secret):
    # text_stream = io.BytesIO(secret)
    bucket.put_object(f"speke/{content_id}", secret)


def acs_oss_get_secret(content_id):
    cipher_text = bucket.get_object(f"speke/{content_id}")
    return cipher_text.read().decode()
