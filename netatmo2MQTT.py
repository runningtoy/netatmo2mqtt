#!/usr/bin/python3

# 2023-07 : ph.larduinat@wanadoo.fr
# Library 3.2.0

# Direct call of Netatmo API with authentication token
# Return a dictionary of body of Netatmo response

import lnetatmo
from geopy.distance import distance
import json
from geopy.distance import geodesic

import paho.mqtt.client as mqtt


def save_json_to_file(params, filename="rawData.json"):
    with open(filename, "w") as file:
        json.dump(params, file, indent=4)


def get_square_parameters(center_lat, center_lon, side_length_km=7):
    half_diagonal = (side_length_km / (2 ** 0.5))  # Halbe Diagonale des Quadrats
    
    # Berechnung der vier Eckpunkte
    #top_left = distance(kilometers=half_diagonal).destination((center_lat, center_lon), 315)
    #bottom_right = distance(kilometers=half_diagonal).destination((center_lat, center_lon), 135)
    top_right = distance(kilometers=half_diagonal).destination((center_lat, center_lon), 45)
    bottom_left = distance(kilometers=half_diagonal).destination((center_lat, center_lon), 225)
    
    params = {
        'lat_ne': top_right.latitude,
        'lon_ne': top_right.longitude,
        'lat_sw': bottom_left.latitude,
        'lon_sw': bottom_left.longitude,
        'filter': 'true'
    }

    #print((f' {top_right.latitude},{top_right.longitude}'))
    #print((f' {bottom_left.latitude},{bottom_left.longitude}'))
    
    return params
  
def publish_mqtt(value):
    mqtt_client = mqtt.Client()
    mqtt_client.connect("192.168.178.100", 1883, 60)
    mqtt_client.publish("netatmo/temperature", value)
    mqtt_client.disconnect()

def process_elements(json_data,center_lat, center_lon, max_distance=3):
    co=0
    total_temparature=0
    for element in json_data:
        #print(f'ID: {element["_id"]}')
        station_lon, station_lat = element['place']['location']
        station_distance = geodesic((center_lat, center_lon), (station_lat, station_lon)).km
        #print(f' station_distance: {station_distance}')
        if(station_distance<max_distance):
          try:
            for measure_id, measure in element["measures"].items():
                if "temperature" in measure["type"]:
                    first_res_value = list(measure["res"].values())[0][0]
                    total_temparature=total_temparature+first_res_value
                    #print(f'Erster Temperaturwert: {first_res_value}')
                    co=co+1
            #print('\n')
          except (TypeError, KeyError):
                pass
    publish_mqtt(total_temparature/co)
    print(f'average Temperaturwert: {total_temparature/co}')


def get_average_temperature(center_latitude, center_longitude, radius=3):   
  try:
    #/tmp/netatmo_last_refresh
    authorization = lnetatmo.ClientAuth(credentialFile="/tmp/credentials.json")
    rawData = lnetatmo.rawAPI(authorization, "getpublicdata",get_square_parameters(center_latitude, center_longitude,2*radius))
    process_elements(rawData,center_latitude, center_longitude,radius)
  except Exception as e:
          print(f"Fehler bei der Netatmo-Authentifizierung: {e}")
          publish_mqtt(-255)
          return
        

if __name__ == "__main__":
   get_average_temperature( 48.1351,  11.5820,3)
