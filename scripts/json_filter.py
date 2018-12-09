import sys
import os
import base64
import json
import pprint
from collections import OrderedDict

# Loop through the directory to make or update posts

year = '2017'
directory = '.' + year + '/processed/json/'
new_directory = '.' + year + '/processed/json-filtered/'

i = 0
for filename in os.listdir(directory):
	# if (i > 10):
	# 	break

	if filename.endswith(".json"):
		path = os.path.join(directory, filename)
		path_destination = os.path.join(new_directory, filename)

		json_file = open(path, 'r')

		property = json.loads(json_file.read())

		if (property.get('place_type_guess') == 'Residence'):

			for key, value in property['values'].items():
				if (value['Ltc_sub-class_code'] == '3600'):
					i += 1
					is_residence = True
					print(str(i) + ' ' + property['Parcel_no'] + ' ' + property['short_address'])

					try:
						destination_json_file = open(path_destination, 'w')
						json.dump(property, destination_json_file, sort_keys=False, indent=2)
						print('new file: ' + property_id)
					except:
						continue

					if (is_residence == True):
						break