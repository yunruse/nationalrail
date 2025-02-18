from requests import get

from argparse import ArgumentParser
from rich import print

from . import api
from requests.exceptions import HTTPError
from .helpers import EXIT_CODES, exit

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
parser.add_argument(
    '--calling',
    default=None, const='line',
    nargs='?', choices=['list', 'line'], metavar='list',
    help="Show intermediary stations (either on a line or on multiple lines with details)")


def time_sig(service: api.ServiceItem, show_orig_time: bool):
    std = service['std']
    etd = service['etd']

    if etd == 'On time':
        return f'[bold green]{std}[/]'
    elif etd == 'Cancelled':
        if show_orig_time:
            return f'[bold red]{std} (CANCELLED)[/]'
        else:
            return f'[bold red]XX:XX[/]'
    else:
        if show_orig_time:
            return f'[bold red]{std} (est. {etd})[/]'
        else:
            return f'[bold red]{etd}[/]'


def station_name(station: api.CallingPoint, show_crs: bool):
    return station['crs'] if show_crs else station['locationName']


def stations_name(stations: list[api.CallingPoint], show_crs: bool):
    return ', '.join(station_name(s, show_crs) for s in stations)


def calling_points(points: list[api.CallingPoint], show_crs: bool, expanded: bool = True):
    if expanded:
        return '\n'.join(f'  - {p['st']} [cyan]{station_name(p, show_crs)}[/] ' for p in points)
    else:
        return ', '.join(f'[cyan]{station_name(p, show_crs)}[/] {p['st']}' for p in points)


def disseminate(
    board: api.StationBoard | api.StationBoardWithDetails,
    show_orig_time: bool,
    show_crs: bool,
    next_stations: bool,
    expand_stops: bool = True,
):
    locName = board.get('locationName')
    services = board.get('trainServices', [])

    if not services or not board.get('areServicesAvailable', False):
        print(
            f"[bold red]No services are available[/] for [bold cyan]{locName}[/].")
        exit(EXIT_CODES.NO_SERVICES, "")

    print(f"Services from [bold cyan]{locName}[/]:")

    for service in services:
        ts = time_sig(service, show_orig_time)
        orig = stations_name(service['origin'], show_crs)
        platform = ''
        if p := service.get('platform'):
            platform = f'[purple italic]Platform {p:<3}[/] '
        dest = stations_name(service['destination'], show_crs)

        arrival = ''
        nextStations = service.get('subsequentCallingPoints', [{}])[
            0].get('callingPoint', [])
        if nextStations:
            dest2 = nextStations[-1]
            arrival = f' {dest2['st']}'

        print(f'- {ts} {platform}{orig} -> [bold cyan]{dest}[/]{arrival}')
        # TODO: service.get('formation')

        if next_stations and len(nextStations) > 1:
            if not expand_stops:
                print('    [bold] stopping at:[/] ', end='')
            print(calling_points(
                nextStations[:-1], show_crs, expanded=expand_stops))

    if nrcc := board.get('nrccMessages'):
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
        parser.exit(
            1, f"ERROR: https://http.cat/{req.status_code}. Try again. \n")

    return req.json()


if __name__ == '__main__':
    args = parser.parse_args()

    try:
        result = api.GetDepBoardWithDetails(args.origin.upper())
    except HTTPError as err:
        msg = f"FATAL: HTTP error https://http.cat/{err.response.status_code}  {err.response.reason}."
        if err.response.status_code == 401:
            exit(EXIT_CODES.BAD_AUTH,
                 f"{msg}\nDid you set a LDBWS_TOKEN? You can obtain one from: http://realtime.nationalrail.co.uk/OpenLDBWSRegistration")

        if err.response.status_code == 400:
            api_msg = err.response.json().get('Message', 'Unknown error')
            exit(2, f'FATAL: {api_msg}')

        exit(1, f"{msg}Try again?")

    # TODO: other station shenaniganseries

    disseminate(result, show_orig_time=args.show_orig_time, show_crs=args.show_crs,
                next_stations=args.calling is not None, expand_stops=args.calling == 'list')
    services = result.get('trainServices', [])
    service = services[0]
