import sys

sys.path.append("../../")

import oss2
import io

from config import ACCESS_KEY_ID, ACCESS_SECRET, OSS_BUCKET_NAME, OSS_ENDPOINT

auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_SECRET)
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)


def acs_oss_create_key(rhb_uuid, cipher_text):
    text_stream = io.StringIO(cipher_text)
    bucket.put_object(f"{rhb_uuid}.txt", text_stream.read())


def acs_oss_get_key(rhb_uuid):
    cipher_text = bucket.get_object(f"{rhb_uuid}.txt")
    return cipher_text.read()
