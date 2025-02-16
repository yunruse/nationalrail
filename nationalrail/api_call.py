from requests import get

from os import getenv
from dotenv import load_dotenv
load_dotenv()
from sys import stderr

from .helpers import exit, EXIT_CODES

BASE = 'https://lite.realtime.nationalrail.co.uk/OpenLDBWS/api/20220120'

def api_call(url: str, params: dict[str, str]):
    """Handler for API calls."""
    auth = ('token', getenv('LDBWS_TOKEN'))

    req = get(BASE + url, params=params, auth=auth)

    # TODO: make these raise an error and exit in __main__
    if req.status_code == 401:
        exit(EXIT_CODES.BAD_AUTH, "ERROR: Unauthorized. Did you set a LDBWS_TOKEN? You can obtain one from: http://realtime.nationalrail.co.uk/OpenLDBWSRegistration")
    if req.status_code != 200:
        exit(1, f"ERROR: https://http.cat/{req.status_code}. Try again?")

    return req.json()