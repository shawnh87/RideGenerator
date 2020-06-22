import requests
import googlemaps
from itertools import combinations
from random import randint
from datetime import datetime
from math import pi, cos, sin, sqrt
import numpy as np
from collections import Counter
import mpu


class RouteGenerate:
    
    def __init__(self, client_id, client_secret, refresh_token, gmaps_key):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.gmaps_key = gmaps_key

    def _get_access_tkn(self):
        refresh_url = "https://www.strava.com/api/v3/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
            "f": 'json'
        }
        resp = requests.post(refresh_url, data=payload)
        print('Refresh Retrieval: ', resp)
        return (resp.json()['access_token'])


    def _get_segs(self, southwest,northeast, min_climb='1', max_climb='4'):
        url = "https://www.strava.com/api/v3/segments/explore?bounds="+\
                southwest.strip('()')+','+ northeast.strip('()')+\
                "&activity_type=riding&min_cat="+min_climb+"&max_cat="+max_climb
        header = {'Authorization': 'Bearer ' + self._get_access_tkn()}
        result = requests.get(url, headers=header)
        print('Segment Retrieval: ', result)
        out = result.json()['segments']
        return {i.get('id'):[tuple(i.get('start_latlng')), tuple(i.get('end_latlng'))] for i in out}


    def _simple_dist(self, p1, p2):
        """euclidean dist. """
        a_sq = (p1[0]-p2[0])**2
        b_sq = (p1[1]-p2[1])**2
        return sqrt(a_sq+b_sq)

    def _reorder(self, p_set, home):
        return p_set[::-1] if np.argmin([self._simple_dist(i,home) for i in p_set])==1 else p_set


    def _rotate(self, start, end):

        vector_hd = start-end
        if end[1]-start[1]<=0:
            rotation = 7*pi/4
        else:
            rotation = pi/4
        rotate = np.array([[cos(rotation), -sin(rotation)], 
                      [sin(rotation), cos(rotation)]])
        return .5*rotate.dot(vector_hd)



    def _get_points_dist(self, id_tuple, home, strava_out):

        points = self._get_waypoints(id_tuple[0],  id_tuple[1], home, strava_out)
        sum_distances = []
        i = 0
        while i < len(points)-1:
            sum_distances.append(mpu.haversine_distance(points[i], points[i+1]))
            i+=1
        return [points, sum(sum_distances)]



    def _get_waypoints(self, part_a, part_b, home, strava_out):


        set1 = strava_out.get(part_a)
        set2 = strava_out.get(part_b)


        home_f = np.array(home)

        p_set1 = self._reorder(set1, home)
        p_set2 = self._reorder(set2, home)

        if p_set1[0][0] < p_set2[0][0]:
            ab = p_set1
            cd = p_set2[::-1]
        else:
            ab = p_set2
            cd = p_set1[::-1]


        d = np.array(cd[1])
        c = np.array(cd[0])
        b = np.array(ab[1])
        a = ab[0]

        result = self._rotate(d, home_f)

        result_c_mid = self._rotate(b,c)


        c_mid = (result_c_mid[0]+c[0], result_c_mid[1]+c[1])
        h_mid = (result[0]+home_f[0], result[1]+home_f[1])
        ##goog may reorder
        points = [home, a, b, c_mid, c, d, h_mid, home]

        return points


    def _construct_rides(self, key_list, strava_out, home, route_size):
        """Places preferences on circuitious rides.
        Of rides closest to desired route size, one ride is randomly chosen"""
    

        options = {'best': [], 'second': [], 'third': []}

        for i,j in enumerate(key_list):
            start_lat_a = strava_out.get(j[0])[0][1]
            end_lat_a = strava_out.get(j[0])[1][1]
            start_lat_b = strava_out.get(j[1])[0][1]
            end_lat_b = strava_out.get(j[1])[1][1]

            if (start_lat_a < home[1] and end_lat_a < home[1]) and (start_lat_b > home[1] and end_lat_b > home[1]):
                options['best'].append(j)

            elif (start_lat_a > home[1] and end_lat_a > home[1]) and (start_lat_b < home[1] and end_lat_b < home[1]):
                options['best'].append(j)

            elif (start_lat_a < home[1] or end_lat_a < home[1]) and (start_lat_b > home[1] or end_lat_b > home[1]):
                options['second'].append(j)

            elif (start_lat_a > home[1] or end_lat_a > home[1]) and (start_lat_b < home[1] or end_lat_b < home[1]):
                options['second'].append(j)
            else:
                options['third'].append(j)

        rides = {}
        if options['best']:
            for i in options['best']:
                points, distance = self._get_points_dist(i, home, strava_out)
                rides[i] = [points, abs(route_size-distance)]
        elif options['second']:
            for i in options['second']:
                points, distance = self._get_points_dist(i, home, strava_out)
                rides[i] = [points, abs(route_size-distance)]
        elif options['third']:
            for i in options['third']:
                points, distance = self._get_points_dist(i, home, strava_out)
                rides[i] = [points, abs(route_size-distance)]
        else:
            print('no rides!')

        sorted_rides = sorted(rides.items(), key = lambda x: x[1][1])

        to_gmap = sorted_rides[:5][randint(0,4)][1][0]
        return to_gmap



    def route_builder(self, sw, ne, home, route_size):

        gmaps = googlemaps.Client(key=self.gmaps_key)
        try:
            out = self._get_segs(sw, ne,'1','4')

            home = tuple((float(i) for i in home.strip('()').split(',')))
            key_list = list(combinations(out.keys() ,2))

            ##error handle here
            ride_waypoints = self._construct_rides(key_list, out, home, route_size)

            route = gmaps.directions(origin=home, 
                                    destination=home,
                                    waypoints=ride_waypoints,
                                    mode='bicycling',
                                    alternatives=True,
                                    units='imperial',
                                    optimize_waypoints =True
                    )

            return route[0]
            
        except:
            print('no ride')
            return None
