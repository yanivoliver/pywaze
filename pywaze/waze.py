import requests
from datetime import timedelta
from collections import namedtuple
import json

Route = namedtuple("Route", ("name", "time"))
Coords = namedtuple("Coords", ("x", "y"))


class AmbiguousQuery(Exception):
    def __init__(self, place, results):
        super().__init__()
        self.results = results
        self.place = place

    def __str__(self):
        return "The query {} yielded multiple results: {}".format(
            self.place, self.results)


class NoResults(Exception):
    def __init__(self, place):
        super().__init__()
        self.place = place

    def __str__(self):
        return "The query {} yielded no results".format(self.place)


def _route(route):
    name = route["response"]["routeName"]
    time = timedelta(seconds=sum(road["crossTime"] for road in route["response"]["results"]))
    return Route(name, time)


def get_coords(place):
    params = {
        "input": place,
        "location":"32.369352595224285,34.9365234375",
        "radius":"2752109.8497292013",
        "sensor": False,
        "key": "AIzaSyBIfV0EMXrTDjrvD92QX5bBiyFmBbT-W8E"
    }

    response = requests.get(
        "https://www.waze.com/maps/api/place/autocomplete/json",
        params=params
    )

    response.raise_for_status()
    data = json.loads(response.text)
    predictions = data["predictions"]

    if not predictions:
        raise NoResults(place)

    if len(predictions) > 1:
        raise AmbiguousQuery(place, [x["description"] for x in predictions])

    reference = predictions[0]["reference"]

    params = {
        "reference": reference,
        "sensor": False,
        "key": "AIzaSyBIfV0EMXrTDjrvD92QX5bBiyFmBbT-W8E"
    }

    response = requests.get(
        "https://www.waze.com/maps/api/place/details/json",
        params=params
    )
    response.raise_for_status()

    location = json.loads(response.text)['result']['geometry']['location']
    return Coords(location['lng'], location['lat'])


def get_routes(source, dest):
    if isinstance(source, str):
        source = get_coords(source)

    if isinstance(dest, str):
        dest = get_coords(dest)

    params = {
        "from": "x:{} y:{}".format(*source),
        "to": "x:{} y:{}".format(*dest),
        "at": 0,
        "returnJSON": True,
        "returnGeometries": True,
        "returnInstructions": True,
        "timeout": 60000,
        "nPaths": 3,
        "options": "AVOID_TRAILS:t",
    }

    response = requests.get(
        "https://www.waze.com/il-RoutingManager/routingRequest",
        params=params
    )
    response.raise_for_status()
    data = json.loads(response.content.decode('utf-8'))

    return [_route(r) for r in data["alternatives"]]
