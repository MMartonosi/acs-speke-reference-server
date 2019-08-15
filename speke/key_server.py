import base64

from flask import Flask

from .key_cache import KeyCache
from .key_generator import KeyGenerator
from .key_server_common import ServerResponseBuilder

import requests


import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "config"))
)


from flask import request

app = Flask(__name__)


@app.route("/test", methods=["POST"])
def server_handler():  # def server_handler():
    """
    This function is the entry point for the SPEKE reference key
    server Lambda. This is invoked from the API Gateway resource.
    """
    try:
        # print(event)
        # # related to aws lambda proxy integration
        # body = event['body']
        # if event['isBase64Encoded']:
        #     body = base64.b64decode(body)

        body = request.data
        cache = KeyCache()
        generator = KeyGenerator()
        response = ServerResponseBuilder(body, cache, generator).get_response()
        print(response)
        return response
    except Exception as exception:
        print(f"Exception {exception}")
        return {"isBase64Encoded": False, "statusCode": 500,
                "headers": {"Content-Type": "text/plain"}, "body": str(exception)}


if __name__ == "__main__":
    app.run(debug=True)
