
from argparse import ArgumentParser

from rich.console import Console

from . import api
from requests.exceptions import HTTPError
from .helpers import EXIT_CODES, exit


parser = ArgumentParser('python -m nationalrail')

parser_s = parser.add_argument_group(
    'Stations',
    """
    These may be the three-letter code (eg KGX) or the name (eg "king's cross london").
    In general the former is less error-prone. You can find it by searching for your station on https://wikidata.org.
    """
)
parser_s.add_argument(
    "orig",
    help="The station to depart from.")

# TODO: figure out nargs='*' api stuff for crslist!
parser_s.add_argument(
    "dest", nargs='?',
    help="The station to arrive at. If not provided, only departures are shown.")

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

console = Console()


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


def next_stations(service: api.ServiceItemWithCallingPoints):
    return service.get('subsequentCallingPoints', [{}])[0].get('callingPoint', [])


def disseminate(
    board: api.StationBoard | api.StationBoardWithDetails,
    show_orig_time: bool,
    show_crs: bool,
    show_next_stations: bool,
    dest: str = None,
    expand_stops: bool = True,
):
    srcName = board.get('locationName')
    services = board.get('trainServices', [])

    if dstName := board.get('filterLocationName'):
        journey = f'from [bold cyan]{srcName}[/] to [bold cyan]{dstName}[/]'
    else:
        journey = f'from [bold cyan]{srcName}[/]'

    if not services or not board.get('areServicesAvailable', False):
        console.print(f"[bold red]No services are available[/] {journey}.")
        exit(EXIT_CODES.NO_SERVICES, "")

    console.print(f'Services {journey}:')

    for service in services:
        ts = time_sig(service, show_orig_time)
        orig = stations_name(service['origin'], show_crs)
        platform = ''
        if p := service.get('platform'):
            platform = f'[purple italic]Platform {p:<3}[/] '

        next = next_stations(service)
        final = next[-1]
        for p in next:
            if p['crs'] == dest and p != final:
                dest_strings = [
                    f'[bold cyan]{station_name(p, show_crs)}[/] {p['st']}',
                    station_name(final, show_crs)
                ]
                break
        else:
            dest_strings = [
                f'[bold cyan]{station_name(final, show_crs)}[/] {final['st']}'
            ]
        console.print(f'- {ts} {platform}{orig} -> {' -> '.join(dest_strings)}')

        # TODO: service.get('formation')

        if show_next_stations and len(next) > 1:
            if not expand_stops:
                console.print('    [bold] stopping at:[/] ', end='')
            console.print(calling_points(
                next[:-1], show_crs, expanded=expand_stops))

    if nrcc := board.get('nrccMessages'):
        console.print('[bold red]Advisories[/]')
        for msg in nrcc:
            console.print(' - ' + msg['Value'].strip())


if __name__ == '__main__':
    args = parser.parse_args()

    try:
        result = api.GetDepBoardWithDetails(args.orig)
    except HTTPError as err:
        msg = f"FATAL: HTTP error https://http.cat/{err.response.status_code}  {err.response.reason}."
        if err.response.status_code == 401:
            exit(
                EXIT_CODES.BAD_AUTH,
                f"{msg}\nDid you set a LDBWS_TOKEN? You can obtain one from: http://realtime.nationalrail.co.uk/OpenLDBWSRegistration")

        if err.response.status_code == 400:
            api_msg = err.response.json().get('Message', 'Unknown error')
            if api_msg == 'Invalid crs code supplied':
                exit(
                    EXIT_CODES.BAD_CRS,
                    'FATAL: The station code(s) you provided were not recognised. Try looking up your station at https://wikidata.org to get the three-letter code (eg KGX).')
            exit(2, f'FATAL: {api_msg}')

        exit(1, f"{msg}Try again?")

    if args.dest:
        args.dest = api.get_crs(args.dest)
        result['trainServices'] = [
            srv for srv in result['trainServices']
            if args.dest in [s['crs'] for s in next_stations(srv)]
        ]

    # TODO: other station shenaniganseries

    disseminate(
        result,
        show_orig_time=args.show_orig_time,
        show_crs=args.show_crs,
        show_next_stations=args.calling is not None,
        dest=args.dest,
        expand_stops=args.calling == 'list',
    )
    services = result.get('trainServices', [])
    service = services[0]
