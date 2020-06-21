# RideGenerator


RideGenerator generates random circuitous routes on a map location of the user’s choosing. 

## Dependencies
#### Google
Googlemaps API key with elevation API activated (moderate usage is covered under the yearly credit provided by google). Project and keys can be found at: https://cloud.google.com/maps-platform

#### Strava
A free Strava account to will grant a client id, access token, and refresh token:
https://developers.strava.com/docs/getting-started/#account

## Runtime
Python 3.8
See requirements.txt

## Additional Files
Construct config.json and api_keys.json as defined in json_key_template.txt

## Details
RideGenerator works by locating popular Strava ride segments within a user submitted bounding box. Of the segments returned by Strava, two segments are selected such that the ability to create a circuitous route is maximized. Starting at a home location, routes are constructed by the GoogleMaps Directions API between various waypoints. In addition to the waypoints at the beginning and end of Strava segments, waypoints are generated to coerce a circuitous path. This is done by creating  points at a 45 degree angle between the vector spanning the end and beginning of Strava segments. In practice this technique works fairly well. 

The application is limited by Strava activity in the user’s locality. In other words, if a user selects a bounding box with zero Strava segments returned, there will not be a route generated.

RideGenerator users provide a target mileage. The application attempts create a route as close to that target as possible while placing preference on routes that circuitous. Circuitous is defined as limited backtracking with the exception of returning to the the start location. Because the key dependency is GoogleMaps, routes are often returned with imperfect characteristics, namely backtracking. No method for erasing such ‘lines’ has been identified. However, for a quick idea of a route in a new location, the RideGenerator is a great tool for cyclists.

GoogleMaps Elevation data is provided as a general idea for the user. Unfortunately the Elevation API is limited to slicing a route up into a maximum of 512 points for elevation measure. As a result the longer the ride generated, the less accurate the elevation will be. View elevation data as a lower bound of true elevation.

## Usage

#### Start Screen:

![alt text](https://github.com/shawnh87/ridegenerator/blob/master/screenshots/ridegenerator.png)

#### Select Bounding Box and Start Location:


![alt text](https://github.com/shawnh87/ridegenerator/blob/master/screenshots/area_selected.png)


#### Generated Route (route directions below map image):

![alt text](https://github.com/shawnh87/ridegenerator/blob/master/screenshots/generated_route.png)



