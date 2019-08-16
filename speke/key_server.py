import os
import sys

from flask import Flask
from oss2.exceptions import NoSuchKey

from .key_cache import KeyCache
from .key_generator import KeyGenerator
from .key_server_common import ServerResponseBuilder

sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
)

from flask import request

app = Flask(__name__)


@app.route("/test", methods=["POST"])
def server_handler():  # def server_handler():
    """
    This function is the entry point for the SPEKE reference key
    server function compute. This is invoked from the API Gateway resource.
    """
    try:
        body = request.data
        cache = KeyCache()
        generator = KeyGenerator()
        response = ServerResponseBuilder(body, cache, generator).get_response()
        print(f"Response {response}")
        return response
    except NoSuchKey as e:
        print(f"Exception {e}")
        return e.body, {'Content-Type': 'text/xml'}
