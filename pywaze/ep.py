import sys
from .waze import get_routes


def main():
    _, source, dest = sys.argv
    routes = get_routes(source, dest)
    for route in routes:
        print("{} - {} minutes".format(route.name, route.time.total_seconds() // 60))
