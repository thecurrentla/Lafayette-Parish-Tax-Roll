import sys
import os
import re
import string
from decimal import *
import pprint
import csv
import json
from collections import OrderedDict

year = '2017'
json_directory = '.' + year + '/processed/json/'
csv_directory = '.' + year + '/processed/csv/'

header_row = ['parcel_no','short_address', 'full_address', 'millages', 'millage_areas']

property_csv = open(csv_directory + 'parcels_filtered.csv', mode='w')
property_csv_writer = csv.DictWriter(property_csv, fieldnames=header_row)
property_csv_writer.writeheader()

i = 0
for filename in os.listdir(json_directory):
	if filename.endswith(".json"):
		path = os.path.join(directory, filename)

		json_file = open(path, 'r')

		property = json.loads(json_file.read(), object_pairs_hook=OrderedDict)
		millages_data = property.get('millages')

		# print(property.get('Parcel_no'))
		# print(property.get('short_address'))
		i += 1

		millages = ''
		millage_slugs = ''
		millage_areas = ''
		for count, millage in millages_data.items():
			millage_slug = millage.get('group_description') + '-' + millage.get('millage')
			millage_slug = millage_slug.replace(' - ', '-')
			millage_slug = millage_slug.replace(' ', '-')
			millage_slug = millage_slug.replace('/', '-')
			millage_slug = millage_slug.replace('.', '-')
			millage_slug = millage_slug.replace('&', '')
			millage_slug = millage_slug.replace('(', '')
			millage_slug = millage_slug.replace(')', '')
			millage_slug = millage_slug.replace('---', '-')
			millage_slug = millage_slug.replace('--', '-')
			millage_slug = millage_slug.lower()

			millage_area = millage.get('place_fips')

			# print(millage)
			# print(millage_slug)
			# print(millage_area)
			millage_slugs = millage_slug + ';' + millage_slugs

			if (millage_area not in millage_areas):
				millage_areas = millage_area + ';' + millage_areas

		millage_slugs = millage_slugs.rstrip(';')
		millage_areas = millage_areas.rstrip(';')

		# print(millage_slugs)
		# print(millage_areas)

		csv_row = OrderedDict.fromkeys('')
		csv_row['parcel_no'] = property.get('Parcel_no')
		csv_row['short_address'] = property.get('short_address')
		csv_row['full_address'] = property.get('full_address')
		csv_row['millages'] = millage_slugs
		csv_row['millage_areas'] = millage_areas

		# print(csv_row)

		property_csv_writer.writerow(csv_row)

		# if (i > 5):
		# 	break