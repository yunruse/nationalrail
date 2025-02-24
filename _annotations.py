from pathlib import Path
from json import loads

LOOKUP_FILE = Path(__file__).parent / 'lookup.json'
LOOKUP: dict[str, str] = loads(LOOKUP_FILE.read_text())


@+GetDepartureBoard(departing_from='crs')
@+GetDepBoardWithDetails(departing_from='crs')
@+GetArrivalBoard(arriving_at='crs')
@+GetArrBoardWithDetails(arriving_at='crs')
@+GetArrivalDepartureBoard(station='crs')
@+GetArrDepBoardWithDetails(station='crs')
def get_crs(crs_or_station_name: str):
    if len(crs_or_station_name) == 3:
        return crs_or_station_name.upper()
    stat = crs_or_station_name.lower().strip()
    if stat in LOOKUP:
        return LOOKUP[stat]
    return crs_or_station_name


@+GetDepartureBoard('filterCrs', 'filterType')
@+GetDepBoardWithDetails('filterCrs', 'filterType')
@+GetArrivalBoard('filterCrs', 'filterType')
@+GetArrBoardWithDetails('filterCrs', 'filterType')
@+GetArrivalDepartureBoard('filterCrs', 'filterType')
@+GetArrDepBoardWithDetails('filterCrs', 'filterType')
def entirely_hidden():
    # IMO, filterCrs is a bit of a kludge
    # that seems to actually delete things. We can hide it.
    pass


# TODO: hide these. they are XML-only? incomprehensible
# del GetFastestDepartures
# del GetFastestDeparturesWithDetails
# del GetNextDepartures
# del GetNextDeparturesWithDetails

# TODO: timeWindow
# TODO: timeOffset
# from datetime import time as Time
# # TODO: figure which actually are times here
# # @+ServiceItemWithCallingPoints['eta']
# @+ServiceDetails['eta', 'sta']
# def time(t: str | None) -> Time | None:
#     return Time(*map(int, t.split(':'))) if t else None
