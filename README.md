# nationalrail

A Python API for National Rail's services, using their modern RESTful Live Departure Boards Web Service (LDBWS) API.

This project is not endorsed by National Rail. It is currently unlicensed, as it is in development.

## Usage

[Register for use with the National Rail site](http://realtime.nationalrail.co.uk/OpenLDBWSRegistration), indicating if this is for personal or corporate use. Once done, National Rail will email you a token. Place this in the environmental var `LDBWS_TOKEN` (e.g. a `.env` file.)

Run as `python -m nationalrail STATION`.

Presently, only departure boards are shown, and they require the CRS (eg `KGX` instead of `"King's Cross"`).

## Developer

Install with Poetry:

```sh
pip install poetry
poetry install
poetry run python -m nationalrail --help
```

### Building the spec

The API functions and types are automatically built from the spec as `api.py`. Some light transformation is done first.

```sh
CONVERT="https://converter.swagger.io/api/convert"
SPEC_URL="https://realtime.nationalrail.co.uk/LDBWS/static/ldbws.json"
HOST="https://lite.realtime.nationalrail.co.uk/OpenLDBWS/api/20220120"
JQ='.servers[0].url = $host | .info.title = "ldbws" | .paths |= with_entries( .key |= sub("^/api/20220120"; ""))'

curl "${CONVERT}?url=${SPEC_URL}" | jq --arg host "$HOST" $JQ > ldbws.json

python tools/wrap_openapi.py ldbws.json > nationalrail/api.py 
```

Note that `wrap_openapi.py` is not feature-complete; it might need a lot of work to adapt to your own purposes.