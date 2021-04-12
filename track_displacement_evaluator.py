#!/usr/bin/env python

'''
Generates the AOI Tracks for coseismic events.

Looks at all acquisitions over the event displacement and calculates the union
for each track. This union defines the bounding box for the AOI Tracks.
'''

import json
import geojson
from shapely.ops import cascaded_union
import constants
import shapely.geometry
from shapely import wkt
from collections import defaultdict
from shapely.geometry import shape
from elasticsearch import Elasticsearch
import urllib3
import lightweight_water_mask

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main(event_polygon, extended_event_polygon):
    print("The extended polygon: {}".format(extended_event_polygon))
    print("The event polygon: {}".format(event_polygon))

    track_data = []
    count = 0
    tracks = defaultdict(dict)
    #GRQ_URL = 'https://100.67.35.28/es/'
    GRQ_URL = 'http://100.67.35.28:9200'

    grq = Elasticsearch(GRQ_URL, verify_certs=False)
    if not grq.ping():
       print("Failed to connect to host.")
       return 1

    doc = {"query":{"filtered":{"query":{"bool":{"must":[{"term":{"dataset.raw":"acquisition-S1-IW_SLC"}}]}},"filter":{"geo_shape":{"location":{"shape":{"type":"polygon","coordinates":extended_event_polygon}}}}}},"size":constants.SIZE,"sort":[{"_timestamp":{"order":"desc"}}],"fields":["_timestamp","_source"]}
    res = grq.search(index=constants.GRQ_ACQUISITION_INDEX, body=doc)

    print("Number of acquisitions over event: {}".format(res['hits']['total']))

    for product in res['hits']['hits']:
        try:
            track_number, polygon, orbit_direction, acq_id = getAcqInfo(product["_source"])
            if track_number in tracks: # If we've already seen this track
                tracks[track_number]["polygons"].append(polygon)
                tracks[track_number]["acq_id"].append(acq_id)
            else: # If this is a new track
                tracks[track_number] = {"polygons": [],"orbit_direction": "", "acq_id": [], "land_area_km2": None}
                tracks[track_number]["polygons"].append(polygon)
                tracks[track_number]["orbit_direction"] = orbit_direction
                tracks[track_number]["acq_id"].append(acq_id)
            count = count + 1
        except:
            print("Failed to parse acquisition metadata for: {}".format(product))
            pass

    extended_polygon = convertToPolygon(extended_event_polygon)

    # Build the track datasets by finding the union of all acquisitions over the same track.
    # Build the AOI dataset by finding the intersection of the displacement estimator polygon and the generated tracks
    for track in tracks.copy():
        tmp = []

        # AOITRACK bbox
        boundary = cascaded_union(tracks[track]['polygons'])
        geojson = shapely.geometry.mapping(boundary)
        track_json = json.dumps(geojson)

        track_poly_land = lightweight_water_mask.get_land_polygons(track_json)
        #print("Track land polygon: " + track_poly_land)
        track_poly_land_json = json.dumps(track_poly_land)
        print("Track land polygon json: ")
        print(track_poly_land)

        # AOI bbox -- starts out with the complete displacement estimator and is carved down
        # to a smaller piece track-by-track
        aoi_track = extended_polygon.intersection(track_poly_land)
        aoi_track_shape = shapely.geometry.mapping(aoi_track)
        aoi_track_json = json.dumps(aoi_track_shape)
        print("AOI TRACK JSON: ")
        print(json.dumps(aoi_track_json, indent=2))

        # Save track data for create-aoi-track job submission
        tmp.append(track)
        tmp.append(aoi_track_json)
        tmp.append(tracks[track]['orbit_direction'])
        track_data.append(tmp)
    #print("This is what is sent out")
    #tmp_intersect_json = shapely.geometry.mapping(tmp_intersect)
    aoi = null
    print(aoi)
    print(track_data)
    print("All the tracks")
    print(tracks.keys())
    return track_data, aoi

# Converts geojson to a shapely polygon
def convertToPolygon(event_polygon):
    event_geojson = {"type": "Polygon", "coordinates": None}
    event_geojson["coordinates"] = event_polygon
    s = json.dumps(event_geojson)
    poly = shape(geojson.loads(s))
    polygon = wkt.loads(str(poly))
    return polygon

def getAcqInfo(product):
    acq_id = product['id']
    track_number = product['metadata']['track_number']
    orbit_direction = product['metadata']['direction']
    polygon = convertToPolygon(product['location']['coordinates'][0])
    return track_number, polygon, orbit_direction, acq_id

# if __name__ == '__main__':
#     polygon = [[[-117.5038333,35.72329970990673],[-117.4962643901115,35.72221596590278],[-117.48960895945737,35.71909553174351],[-117.48467004734442,35.71431498626769],[-117.48204325618994,35.70845117072158],[-117.48204496162863,35.7022115022954],[-117.48467436566698,35.69634857692398],[-117.48961387007292,35.69156939527501],[-117.49626759528836,35.68845016044506],[-117.5038333,35.687366890093266],[-117.51139900471165,35.68845016044506],[-117.51805272992709,35.69156939527501],[-117.52299223433303,35.69634857692398],[-117.52562163837138,35.7022115022954],[-117.52562334381005,35.70845117072158],[-117.52299655265558,35.71431498626769],[-117.51805764054264,35.71909553174351],[-117.5114022098885,35.72221596590278],[-117.5038333,35.72329970990673]]]
#     extended_event_polygon = [[[-117.503833,36.64857],[-117.102053,36.591021],[-116.75033,36.425554],[-116.491903,36.172726],[-116.4345125703697,36.04067562430324],[-116.3603356270024,35.67265830876247],[-116.362294,35.536149],[-116.503804,35.229571],[-116.763866,34.980501],[-117.110889,34.81834],[-117.503833,34.762097],[-117.896777,34.81834],[-118.243801,34.980501],[-118.503863,35.229571],[-118.645372,35.536149],[-118.650072,35.863695],[-118.515764,36.172726],[-118.257337,36.425554],[-117.905614,36.591021],[-117.503833,36.64857]]]
#     track_data = main(polygon, extended_event_polygon)
#     print(track_data)
