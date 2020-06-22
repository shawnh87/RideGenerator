from flask import Flask, render_template
from forms import RouteBuildForm
import matplotlib.pyplot as plt
import numpy as np
import requests
from build import RouteGenerate
import utils
import json


###keys located in config
with open('api_keys.json') as j:
    keys =  json.load(j)


with open('config.json') as c:
    secret = json.load(c)


app = Flask(__name__)
app.config['SECRET_KEY'] = secret['SECRET_KEY']



@app.route('/', methods=['GET', 'POST'])
def index():
    context = {
        "key": keys['gmaps_key'],       
    }

    form = RouteBuildForm()

    if form.validate_on_submit():

        builder = RouteGenerate(**keys)
        route = builder.route_builder(form.southwest.data, form.northeast.data, form.home.data, form.distance.data)

        if route:
            context['points'] = repr(route['overview_polyline'].get('points')).replace("'",'')
            context['dist'] = sum([i.get('distance').get('value')*0.0006213712 for i in route['legs']])

            center = utils.get_center(route)
            context['center_lat'] = float(center.get('lat'))
            context['center_lng'] = float(center.get('lng'))
            
            context['ele'] = utils.get_elevation(route['overview_polyline'].get('points'))
            context['x'] =  list(np.arange(0, context['dist'], context['dist']/512))
            context['gain'] = utils.get_total_gain(context['ele'])
            
            context['directions'] = utils.get_directions(route)
            start = route['legs'][0].get('start_location')
            
            context['start_lat'] = start.get('lat')
            context['start_lng'] = start.get('lng')

        else:
            context['none'] = 'No ride found! Please Try again!'

    return render_template('main.html', form=form, context=context)


if __name__== '__main__':
    app.run(debug=False)

