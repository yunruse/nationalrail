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

### TODO: building the API spec

The API can be automatically built from spec. Hasn't been done yet. Needs work to figure out the breadth of it.

```sh
pip install openapi-generator

CONVERT="https://converter.swagger.io/api/convert"
SPEC_URL="https://realtime.nationalrail.co.uk/LDBWS/static/ldbws.json"
HOST="https://lite.realtime.nationalrail.co.uk/OpenLDBWS"

curl "${CONVERT}?url=${SPEC_URL}" | jq --arg host "$HOST" '.servers[0].url = $host | .info.title = "ldbws"' > ldbws.json
poetry run openapi-generator-cli generate -g python --additional-properties=packageName=ldbws -i ldbws.json
# the jq is necessary because the spec references `localhost`
```