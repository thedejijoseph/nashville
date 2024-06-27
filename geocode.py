

# # contains geocoding-related scripts

# import json, time

# import pandas
# from geopy.geocoders import ArcGIS

# import data_fetcher as dff
# # import data_writer as dw


# data = dff.read_data(filename='data-231217-2737.txt')

# appts = [dff.extract_apartment_data(appt) for appt in data]
# df = pandas.DataFrame(appts)

# # get all region_text values
# region_texts = df['region_text'].unique()

# # prepare api request

# records = {}

# geocoder = ArcGIS()

# for region in region_texts:
#     try:
#         result = geocoder.geocode(region)
#         records[region] = result.raw
#         print(f'retrieved geocode for {region}')
#     except Exception as e:
#         print(e)
#         records[region] = {}
#     time.sleep(2)

# geocode_file = df.create_filename(name_prefix="geocode-", file_ext="json")
# json_dump = json.dumps(records)
# fl = open(geocode_file, 'w')
# fl.write(json_dump)
# fl.close()


import numpy as np
import json, time
import pandas
from geopy.geocoders import ArcGIS
from shapely.geometry import shape, Point
import data_fetcher as dff

geocoder = ArcGIS()
geojson_data = open('lagos.geojson', 'r')
lagos = json.loads(geojson_data.read())

lgas = {}
for feat in lagos['features']:
    try:
        if feat['properties']['Name']:
            lgas[feat['properties']['Name']] = feat
    except:
        pass

def create_geocode_cache():
    data = dff.read_data(filename='data-231217-2737.txt')
    appts = [dff.extract_apartment_data(appt) for appt in data]
    df = pandas.DataFrame(appts)
    region_texts = list(df['region_text'].unique())
    records = {}
    
    for region in region_texts:
        try:
            result = geocoder.geocode(region)
            records[region] = result.raw
            print(f'retrieved geocode for {region}')
        except Exception as e:
            print(e)
            records[region] = {}
        time.sleep(2)

    geocode_file = dff.create_filename(name_prefix="geocode", file_ext="json")
    json_dump = json.dumps(records)
    fl = open(geocode_file, 'w')
    fl.write(json_dump)
    fl.close()

def load_geocode_cache(filename="geocode-240624-4153.json"):
    geocode_cache_file = open(filename, 'r')
    arcgis_geocode_cache = json.loads(geocode_cache_file.read())

    return arcgis_geocode_cache

def geocode(region):
    cache = load_geocode_cache()

    geocode_result = cache.get(region, None)
    if geocode_result is None:
        print(f"region '{region}' not found in cache, attempting to fetch")
        try:
            region = geocoder.geocode(region)
            print(region)
            return region['location']
        except Exception as e:
            # raise e
            print(f"failed to retrieve geocode for {region}")
            return {'x': 'not-available', 'y': 'not-available'}
    else:
        try:
            return geocode_result.get('location', None)
        except:
            print(region)
            print(geocode_result)

def get_lga(x, y):
    likely_locations = []
    for feature in lagos['features']:
        polygon = shape(feature['geometry'])
        point = Point(x, y)
        if polygon.contains(point):
            likely_locations.append(feature)
    
    if len(likely_locations) > 0:
        return likely_locations[0]['properties']['Name']
    else:
        return 'cannot-locate'

def random_point_in_lga(lga):
    if lga != 'cannot-locate':
        lga = lgas[lga]

        while True:
            polygon = shape(lga['geometry'])
            minx, miny, maxx, maxy = polygon.bounds

            x = np.random.uniform(minx, maxx, 1)
            y = np.random.uniform(miny, maxy, 1)
            point = Point(x, y)
            if polygon.contains(point):
                return {'x': x[0], 'y': y[0]}
    else: 
        return {'x': 0, 'y': 0}
