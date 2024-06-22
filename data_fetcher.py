"""
Data Fetcher

Simple script to fetch data from Jiji for Project Nashville

Project Nashville is setup to answer one question with the help of interactive
data visualisation: what are the most expensive areas to live in Lagos?
"""

import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import requests

from environs import Env

env = Env()
env.read_env()

DATA_URL = env('DATA_URL')
url_object = urlparse(DATA_URL)



def create_filename(name_prefix='data', file_ext='txt'):
  """
  Creates a new string in the format 'data-yymmdd-mmss'.

  Args:
    data_prefix: Optional prefix to add before the timestamp (default: "data").

  Returns:
    A string in the format 'data-yymmdd-mmss'.
  """
  now = datetime.now()
  year = now.strftime("%y")
  month = now.strftime("%m")
  day = now.strftime("%d")
  minute = now.strftime("%M")
  second = now.strftime("%S")

  timestamp = f"{year}{month}{day}-{minute}{second}"
  return f"{name_prefix}-{timestamp}.{file_ext}"

def flatten_json(data, parent_key=''):
    """
    Flattens a nested JSON dictionary, separating keys with "-".

    Args:
        data: The nested JSON dictionary.
        parent_key: Optional parent key prefix for nested elements (default: "").

    Returns:
        A flat dictionary with hyphen-separated keys.
    """
    flattened_data = {}
    for key, value in data.items():
        new_key = parent_key + "-" + key if parent_key else key
        if isinstance(value, dict):
            flattened_data.update(flatten_json(value, new_key))
        else:
            flattened_data[new_key] = value
    return flattened_data

def transform_period(object):
    if object == 'per annum':
        return 'annually'
    elif object == 'per month':
        return 'monthly'
    else:
        return 'undefined'

def transform_state(object):
    return object

def extract_apartment_data(advert_object):
    # source is an advert object
    source = flatten_json(advert_object)

    labels = [
        'price', 'period_raw', 'period', 'region_text', 'region', 'region_parent', 'state',
        'description', 'title', 'slug', 'url', 'status', 'property_size', 'property_size_unit',
        'furnished', 'bedrooms', 'bathrooms'
        ]
    d = {}

    d['price'] = source.get('price_obj-value', None)
    d['period_raw'] = source.get('price_obj-period', None)
    d['period'] = transform_period(d['period_raw'])
    d['region_text'] = source.get('region_item_text', None)
    d['region'] = source.get('region_name', None)
    d['region_parent'] = source.get('region_parent_name', None)
    d['state'] = transform_state(d['region_parent'])
    d['description'] = source.get('short_description', None)
    d['title'] = source.get('title', None)
    d['slug'] = source.get('slug', None)
    d['url'] = source.get('url', None)
    d['status'] = source.get('category_slug', None)

    # attributes
    attributes = source.get('attrs')
    if attributes:
      for attr in attributes:
        if attr['name'] == 'Property size':
            d['property_size'] = attr['value']
            d['property_size_unit'] = attr['unit']
        if attr['name'] == 'Furnishing':
            d['furnished'] = attr['value']
        if attr['name'] == 'Bedrooms':
           d['bedrooms'] = attr['value']
        if attr['name'] == 'Bathrooms':
           d['bathrooms'] = attr['value']

    # replace non-existent fields with None
    missing = set(labels) - set(d.keys())
    for label in missing:
        d[label] = None
    
    return d

def fetch_data(write_to='disk'):
    # separate url & query
    data_url = url_object._replace(query=None).geturl()
    data_query = parse_qs(url_object.query)

    if write_to == 'disk':
        filename = create_filename()
        with open(filename, 'a') as f:
            for i in range(1000):
                print(f'fetching page {i}')
                data_query['page'] = i
                r = requests.get(data_url, params=data_query)
                raw_data = r.text
                data = json.loads(raw_data)
                try:
                    if data['status'] == 'ok':
                        apartments = json.dumps(data['adverts_list']['adverts'])
                        f.write(apartments + '\n')
                except: 
                    print(f'cannot parse page {i}')
    else:
        print(f'cannot write to {write_to}')
        return

def read_data(source='disk', filename=None):
    if source == 'disk':
        if not filename:
            filename = input("enter the filename: ")

        all_objects = []
        with open(filename, "r") as f:
            for line in f:
                # Try to convert each line to a list of JSON objects
                try:
                    line_objects = json.loads(line)
                except Exception as e:
                    print(f"Error while processing line: {line}. Skipping. Exception: {e}")
                    continue
                # Add the list of objects from the line to the overall list
                all_objects.extend(line_objects)
        
        return all_objects
    else:
        print('cannot find data source')
        return None

if __name__ == '__main__':
    fetch_data()
