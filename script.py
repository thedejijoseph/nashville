
#how to run

# if data has been downloaded to a file already,

import data_fetcher as df
import data_writer as dw

# labels = [
#         'price', 'period_raw', 'period', 'region_text', 'region', 'region_parent', 'state',
#         'description', 'title', 'slug', 'url', 'status', 'property_size', 'property_size_unit',
#         'furnished', 'bedrooms', 'bathrooms'
#         ]

data = df.read_data(filename='data-231217-2737.txt')
appts = [df.extract_apartment_data(appt) for appt in data]
dw.to_csv(appts)

# for appt in appts:
#     count=0; 
#     if len(appt.keys()) < 17: 
#         count+=1
#         print("\n\n", appt)
#         print("\n>>", appt.keys())
#         print(set(labels) - set(appt.keys()))
#         if count == 4:
#             break
