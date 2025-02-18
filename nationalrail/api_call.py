from requests import get

from os import getenv
from dotenv import load_dotenv
load_dotenv()

BASE = 'https://lite.realtime.nationalrail.co.uk/OpenLDBWS/api/20220120'

def api_call(url: str, params: dict[str, str]) -> dict[str]:
    """Handler for API calls."""
    r = get(BASE + url, params=params, auth=('token', getenv('LDBWS_TOKEN')))
    r.raise_for_status()
    return r.json()