import sys

sys.path.append("../../")

import oss2

# from config import get_access_secret
from itertools import islice

from config import ACCESS_KEY_ID, COUNTER


import pdb

pdb.set_trace()

# get_config()


# access_key, secret_key = get_access_secret()
# auth = oss2.Auth(access_key, secret_key)
# bucket = oss2.Bucket(auth, "oss-cn-shanghai.aliyuncs.com", "keys-test-bucket")
# for item in islice(oss2.ObjectIterator(bucket), 10):
#     print(item)
#     print(item.key)
