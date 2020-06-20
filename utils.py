import numpy as np
import googlemaps
import json


with open('api_keys.json') as j:
    keys =  json.load(j)


def get_center(gmap_output):
    ne = gmap_output['bounds']['northeast']
    sw = gmap_output['bounds']['southwest']
    return {'lat': (ne['lat']+sw['lat'])/2, 'lng': (ne['lng']+sw['lng'])/2}


def get_elevation(path):
    """512 is max splits allowed by googlemaps elevation api"""

    gmaps = googlemaps.Client(key=keys['gmaps_key'])
    elevation =  gmaps.elevation_along_path(path, 512)
    return [round(i.get('elevation'),2) for i in elevation]


def get_total_gain(elevation):
    gain = 0
    for i, k in enumerate(elevation):
        if i!=len(elevation)-1:
            diff = elevation[i+1]-elevation[i]
            if diff > 0:
                gain+=diff 
    return gain


def get_directions(output):
    directions = []
    for i in output['legs']:
        if i.get('steps'):
            for j in i.get('steps'):
                directions.append(j.get('html_instructions'))
    return directions