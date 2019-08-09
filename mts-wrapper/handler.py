"""
local HTTP service, which serves as authentication service in playing HLS standard
encryption video, to issue and verify MtsHlsUriToken token - which serves as the token
to request the decryption key.

General flow:
    - Video player accesses the URI in the EXT-X-KEY tag in the video manifest file.
    - URI is a description key build by OBS BLL.
    - While requesting decryption, the player must carry some authentication
    information recognized by the business side
    - The business side issues a token to the player, which carries the token when
    requesting the decryption key, and the business side checks the validity of the
    token.
"""
from aliyunsdkcore.client import AcsClient
from aliyunsdkkms.request.v20160120 import DecryptRequest

import cgi
import json
import base64
import urllib.parse
from urllib.parse import urlparse, parse_qs
import configparser

from http.server import BaseHTTPRequestHandler

config = configparser.ConfigParser(allow_no_value=True)
ACCESS_KEY_ID = config.get("USER_INFO", "access_key_id")
ACCESS_SECRET = config.get("USER_INFO", "access_secret")
REGION_ID = config.get("USER_INFO", "region_id")

client = AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, REGION_ID)


class AuthorizationHandler(BaseHTTPRequestHandler):
    def do_get(self):
        self.check()
        self.set_header()
        ciphertext = self.get_ciphertext()
        plaintext = self.decrypt_ciphertext(ciphertext)
        print(f"Plaintext {plaintext}")
        key = base64.b64decode(plaintext)
        print(f"Key {key}")

    def do_post(self):
        pass

    def check(self):
        pass

    def set_header(self):
        pass

    def get_ciphertext(self):
        path = urlparse(self.path)
        query = parse_qs(path.query)
        return query.get("Ciphertext")[0]

    def decrypt_ciphertext(self, ciphertext):
        request = DecryptRequest.DecryptRequest()
        request.set_CiphertextBlob(ciphertext)
        response = client.do_action_with_exception(request)
        json_resp = json.loads(response)
        return json_resp["Plaintext"]


if __name__ == "__main__":
    from http.server import HTTPServer
    print("Staring development server ...")
    server = HTTPServer(("127.0.0.1", "8888"), AuthorizationHandler)
    server.serve_forever()
