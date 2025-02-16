from enum import IntEnum
from requests import get

from argparse import ArgumentParser
from rich import print

parser = ArgumentParser('python -m nationalrail')
parser.add_argument(
    "origin",
    help="Must be the three-letter code, eg KGX.")
parser.add_argument(
    '--crs',
    dest='show_crs', action='store_true',
    help="Show three-letter station codes ('crs'), e.g. KGX, instead of names.")
parser.add_argument(
    '--compress-delay',
    dest='show_orig_time', action='store_false',
    help="Display train time in red, without the original time.")


BASE = 'https://lite.realtime.nationalrail.co.uk/OpenLDBWS/api/20220120'
DEPARTURES = BASE + '/GetDepartureBoard/{origin}'

class EXIT_CODES(IntEnum):
    BAD_AUTH = 3
    NO_SERVICES = 4

def time_sig(service: dict, show_orig_time: bool):
    std = service['std']
    etd = service['etd']
    
    if etd == 'On time':
        return f'[bold green]{std}[/]'
    elif show_orig_time:
        return f'[bold red]{std} (est. {etd})[/]'
    else:
        return f'[bold red]{etd}[/]'
    
Station = dict

def station_name(stations: list[Station], show_crs: bool):
    if len(stations) > 1:
        raise NotImplementedError('Multiple stations not yet supported')
    s = stations[0]
    return s['crs'] if show_crs else s['locationName']

def disseminate(
    json: dict,
    show_orig_time: bool,
    show_crs: bool
):
    locName = json.get('locationName')
    services = json.get('trainServices', [])

    if not services or not json.get('areServicesAvailable', False):
        print(f"[bold red]No services are available[/] for [bold cyan]{locName}[/].")
        exit(EXIT_CODES.NO_SERVICES)

    print(f"Services for [bold cyan]{locName}[/]:")

    for service in services:
        ts = time_sig(service, show_orig_time)
        orig = station_name(service['origin'], show_crs)
        dest = station_name(service['destination'], show_crs)
        
        print(f'- {ts} {orig} -> [bold cyan]{dest}[/]')

    # TODO: disseminate.
    # nrccMessages looks useful too!

    if nrcc := json.get('nrccMessages'):
        print('[bold red]Advisories[/]')
        for msg in nrcc:
            print(' - ' + msg['Value'].strip())

def fetch(url):
    from os import getenv
    from dotenv import load_dotenv
    load_dotenv()
    auth = ('token', getenv('LDBWS_TOKEN'))

    req = get(url, auth=auth)
    if req.status_code == 401:
        parser.exit(EXIT_CODES.BAD_AUTH, "ERROR: Unauthorized. Did you set a LDBWS_TOKEN? You can obtain one from: http://realtime.nationalrail.co.uk/OpenLDBWSRegistration\n")
    if req.status_code != 200:
        parser.exit(1, f"ERROR: https://http.cat/{req.status_code}. Try again. \n")

    return req.json()

if __name__ == '__main__':
    args = parser.parse_args()
    
    url = DEPARTURES.format(origin=args.origin.upper())
    json = fetch(url)

    disseminate(json, show_orig_time=args.show_orig_time, show_crs=args.show_crs)
    services = json.get('trainServices', [])
    service = services[0]
