from pathlib import Path
from json import loads

LOOKUP_FILE = Path(__file__).parent / 'lookup.json'
LOOKUP: dict[str, str] = loads(LOOKUP_FILE.read_text())


@+GetDepartureBoard('crs')
@+GetArrivalBoard('crs')
@+GetArrivalDepartureBoard('crs')
@+GetArrBoardWithDetails('crs')
@+GetDepBoardWithDetails('crs')
@+GetArrDepBoardWithDetails('crs')
@+GetFastestDepartures('crs')
@+GetFastestDeparturesWithDetails('crs')
@+GetNextDepartures('crs')
@+GetNextDeparturesWithDetails('crs')
@+GetServiceDetails('crs')
def get_crs(crs_or_station_name: str):
    if len(crs_or_station_name) == 3:
        return crs_or_station_name.upper()
    stat = crs_or_station_name.lower().strip()
    if stat in LOOKUP:
        return LOOKUP[stat]
    return crs_or_station_name

# TODO: timeWindow
# TODO: timeOffset
# from datetime import time as Time
# # TODO: figure which actually are times here
# # @+ServiceItemWithCallingPoints['eta']
# @+ServiceDetails['eta', 'sta']
# def time(t: str | None) -> Time | None:
#     return Time(*map(int, t.split(':'))) if t else None
