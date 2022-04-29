# Create your views here.
from distutils.command.build import build
from email.headerregistry import Address
import encodings
from .forms import ValuationAPIForm
from rest_framework import viewsets 
from rest_framework.decorators import api_view 
from django.core import serializers 
from rest_framework.response import Response 
from rest_framework import status 
from django.http import JsonResponse 
from rest_framework.parsers import JSONParser 
from .models import ValuationAPI
from .serializer import ValuationSerializers
import pandas as pd
import requests
from fuzzywuzzy import fuzz

import pickle
import json 
import numpy as np 
from sklearn import preprocessing 
import pandas as pd 
from django.shortcuts import render, redirect 
from django.contrib import messages 

class CustomerView(viewsets.ModelViewSet): 
    queryset = ValuationAPI.objects.all() 
    serializer_class = ValuationSerializers

def status(df):
    #rf_model = pickle.load(open("RandomForestRegressor_model2.pkl", 'rb'))
    xb_model = pickle.load(open("XGBRegressor_model.pkl", 'rb'))
    #cb_model = pickle.load(open("CatBoostRegressor_model.pkl", 'rb'))
    std_scaler = pickle.load(open("std_scaler.pkl", 'rb'))
    df_scaled = std_scaler.transform(df)
    #y_pred_rf = rf_model.predict(df_scaled)
    #y_pred_cb = cb_model.predict(df_scaled)
    y_pred_xb = xb_model.predict(df_scaled)
    y_pred =  y_pred_xb# (y_pred_rf + + y_pred_cb) / 3

    result = y_pred * df['area'][0]

    error_percent = 0.08
    from_cost = float(result - (result * error_percent))
    to_cost = float(result + (result * error_percent))

    return [str(int(y_pred.round(-3))) + ' ₸', str(int(result.round(-4))) + ' ₸', f'{round(from_cost/1000000, 1)} - {round(to_cost/1000000, 1)} млн ₸']

def input_address(input, i=0):

    apikey = ["30d15fb0-f398-47fb-b8aa-98876c2b8c6b", "24f0b1b4-c811-4f01-8b8e-b4d02d90dc95",
              "b3ef816b-e742-4ca8-ac52-d8a50cf3e4da", "e6a2f383-92a7-40bb-9906-d8caac65e25a",
              "f506b684-7f58-4edc-a1a6-edbb9970b706", "8b4a0e4d-c149-4c01-a0df-d336d07d8ce1",
              "1dd25d5c-4345-4ec8-a74c-cbedd10e5292"]

    url = f"https://geocode-maps.yandex.ru/1.x/"

    address = f'Нур-Султан (Астана), {input}'

    response = requests.get(url, params=dict(format="json", apikey=apikey[i], geocode=address))

    if response.status_code == 200:

        data = response.json()["response"]["GeoObjectCollection"]["featureMember"]

        if data:
            coordinates = data[0]["GeoObject"]["Point"]["pos"].split(" ")
            coordinates[0], coordinates[1] = float(coordinates[0]), float(coordinates[1])

            return coordinates

        else:

            all_coords_df = pd.read_csv('all_coords.csv', sep='*', encoding="utf-8")

            similarity = 60
            coordinates = []

            for i in range(len(all_coords_df['address'])):

                location = all_coords_df['address'][i]

                if fuzz.WRatio(address, location) > similarity:

                    similarity = fuzz.WRatio(address, location)
                    coordinates.append(all_coords_df['lon'][i])
                    coordinates.append(all_coords_df['lat'][i])

            if coordinates:
                return coordinates

            else:
                return 'Address not found'

    else:
        if i < len(apikey)-1:
            input_address(input, i+1)
        else:
            raise ConnectionError

def find_distance_to_objects(lat, lon, i=0):

    river_region = '(51.1035868, 71.3768206, 51.1609449, 71.5328273)'
    obj_distance = 200
    objects = {'amenity': ['cafe', 'restaurant', 'kindergarten', 'school', 'college', 'university', 'hospital', 'clinic', 'theatre', 'arts_centre', 'townhall'],
               'shop': ['supermarket', 'mall'],
               'waterway': ['river'],
               'leisure': ['park'],
               'tourism': [],
               'sport': [],
               }

    s = ''

    row = {
        'cafe': 0,
        'restaurant': 0,
        'kindergarten': 0,
        'school': 0,
        'college': 0,
        'university': 0,
        'hospital': 0,
        'clinic': 0,
        'theatre': 0,
        'arts_centre': 0,
        'townhall': 0,
        'supermarket': 0,
        'mall': 0,
        'park': 0,
        'river': 0,
        'tourism': 0,
        'sport': 0,
    }

    for type in objects:

        if type == 'waterway':
            for obj in objects[type]:
                s += f"way[{type}={obj}][int_name='Ishim']{river_region}(around:{obj_distance}, {lat}, {lon});\n"

        elif type in ['sport', 'tourism']:
            s += f'nwr[{type}](around:{obj_distance}, {lat}, {lon});\n'

        else:
            for obj in objects[type]:
                s += f'nwr[{type}={obj}](around:{obj_distance}, {lat}, {lon});\n'

    overpass_query = f"""
      [out:json];
      area[name="Нур-Султан"];
      ({s});
      out center;
      """

    overpass_url = ["https://maps.mail.ru/osm/tools/overpass/api/interpreter", f"http://overpass-api.de/api/interpreter"]

    response = requests.get(overpass_url[i], params={'data': overpass_query})

    if response.status_code == 200:

        data = json.loads(response.text)

        if not data:
          return row

        for element in data['elements']:
          for tag in element['tags']:
            if tag in ['sport', 'tourism']:
                row[tag] = 1
            elif tag in ['amenity', 'shop', 'waterway', 'leisure']:
                if element['tags'][tag] in objects[tag]:
                    row[element['tags'][tag]] = 1

        return row
    else:
        if i < len(overpass_url) - 1:
            find_distance_to_objects(lat, lon, i+1)
        else:
            raise ConnectionError

def HomeView(request):
    return render(request, 'restapi/Example_home.html')

def FormView(request):
    if request.method=='POST':
        form=ValuationAPIForm(request.POST or None)
        if form.is_valid():
            model_inputs = pd.read_csv('model_inputs.csv', sep='*', encoding="utf-8")
            inputs = {
            'rooms': form.cleaned_data['rooms'],
            'ceiling': form.cleaned_data['ceiling'],
            'address': form.cleaned_data['address'],
            'building_year' : form.cleaned_data['building_year'],
            'floor' : form.cleaned_data['floor'],
            'total_floors' : form.cleaned_data['total_floors'],
            'area' : form.cleaned_data['area'],
            'region': form.cleaned_data['region'],
            'renovation' : form.cleaned_data['renovation'],
            'toilet' : form.cleaned_data['toilet'],
            'balcony' : form.cleaned_data['balcony'],
            'building_type' : form.cleaned_data['building_type'],
            'complex_class' : form.cleaned_data['complex_class'],
            'security' : form.cleaned_data['security'],
            }
            for input in inputs.keys():
                if input == 'address':

                    model_inputs['address_lat'] = input_address(inputs[input])[1]
                    model_inputs['address_lon'] = input_address(inputs[input])[0]

                    city_objs = find_distance_to_objects(model_inputs['address_lat'][0], model_inputs['address_lon'][0])

                    for obj in city_objs.keys():
                        model_inputs[obj] = city_objs[obj]

                elif input in ['region', 'renovation', 'toilet', 'balcony', 'building_type', 'complex_class', 'security']:
                    if inputs[input] != ' ':
                        model_inputs[inputs[input]] = 1

                #elif input == 'security':
                 #   for sec_input in inputs[input]:
                  #      model_inputs[sec_input] = 1

                else:
                    model_inputs[input] = inputs[input]
            result = status(model_inputs)
            return render(request, 'restapi/Example.html', {"data0" : result[0], 'data1' : result[1], 'data2' : result[2], 'form' : form}) 
    form=ValuationAPIForm()
    return render(request, 'restapi/Example.html', {'form' : form})