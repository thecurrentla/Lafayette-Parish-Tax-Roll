import sys
import os
from decimal import *
import pprint
import csv
import json
from collections import OrderedDict
from random import shuffle
import usaddress #https://github.com/datamade/usaddress

year = '2017'
directory = '.' + year + '/processed/json/'

towns = ["Broussard","Carencro","Duson","Lafayette","Milton","Ossun","Scott","Youngsville"]

def normalize_address(address):
	# Strip spaces
	address = address.strip()

	# Fix PO Box inconsistency
	address = address.replace("P O BOX ","PO BOX ")

	return address

def remove_address_zip(address):
	# Remove Zip code
	address = address.rstrip('0123456789-').strip()

	return address

def clean_up_address(address):
	# @todo: consider https://github.com/GreenBuildingRegistry/usaddress-scourgify

	# Remove Zip code
	address = remove_address_zip(address)

	# Title Case
	address = address.title()

	# Fix PO Box case
	address = address.replace("P O Box ","PO Box ")
	address = address.replace("Po Box ","PO Box ")
	address = address.replace("Po Drawer ","PO Drawer ")

	# Remove abbreviations
	## Directions
	address = address.replace(" S "," South ")
	address = address.replace(" N "," North ")
	address = address.replace(" E "," East ")
	address = address.replace(" W "," West ")
	address = address.replace(" SE "," Southeast ")
	address = address.replace(" NE "," Northeast ")
	address = address.replace(" SW "," Southwest ")
	address = address.replace(" NW "," Northwest ")
	address = address.replace(" Se "," Southeast ")
	address = address.replace(" Ne "," Northeast ")
	address = address.replace(" Sw "," Southwest ")
	address = address.replace(" Nw "," Northwest ")

	## Street types
	### "Street" requires special case to avoid "Street Mary Street"
	# for town in towns:
	# 	address = address.replace(" St " + town, " Street " + town)

	## Other street types
	address = address.replace(" Ave"," Avenue ")
	address = address.replace(" Blvd"," Blvd. ")
	address = address.replace(" Cir"," Circle ")
	address = address.replace(" Ct"," Court ")
	address = address.replace(" Cv"," Cove ")
	address = address.replace(" Dr"," Drive ")
	address = address.replace(" Hwy"," Highway ")
	address = address.replace(" Ln"," Lane ")
	address = address.replace(" Pkwy"," Parkway ")
	address = address.replace(" Pl"," Place ")
	address = address.replace(" Plz"," Plaza ")
	address = address.replace(" Rd"," Road ")
	address = address.replace(" Rw"," Row ")
	# address = address.replace(" St"," Street")
	address = address.replace(" Trl"," Trail")
	address = address.replace(" Thru"," Throughway")

	## Apartments, Suites, etc
	address = address.replace(" Ste ",", Suite ")
	address = address.replace(" Apt ",", Apt. ")
	address = address.replace(" Lot ",", Lot ")

	## Add commas after cities/fix state abbr. case
	# for town in towns:
	# 	address = address.replace(town + " La", town + ", LA")

	return address

def guess_place_type(address):
	type = ''

	# Check if in the state
	if (not address.endswith("LA") and not address.endswith("La")):
		type = 'Out of State'
		return type

	# Check if in the parish
	for town in towns:
		if town in address:
			type = 'In Parish'

	if (type != 'In Parish'):
		type = 'Out of Parish'
		return type

	# Check for PO Boxes
	if ("PO Box" in address or "PO Drawer" in address):
		type = 'Post Office Box'

	# Check for Government Buildings
	if (" City Of " in address or " City of " in address):
		type = 'Government Property'

	if (" Lafayette City Parish Consolidated Government " in address):
		type = 'Government Property'

	if (" Inc " in address or " Llc " in address):
		type = 'Commercial Property'

	# Check for apartments
	if (" Apt. " in address):
		type = 'Apartment'

	# If it's still marked as "In Parish", it's probably a residence?
	if (type == 'In Parish'):
		type = 'Residence'

	return type;

def split_address_zip(address):
	zipless_address = remove_address_zip(address)
	zip = address.replace(zipless_address, '').strip()

	return zip

def split_address_city_state(full_address):
	for town in towns:
		if town in full_address:
			street_address = full_address.replace(town,'').replace(', LA','').strip()
			split_address = {"street_address": street_address, "city": town, "state": "LA"}
			return split_address

def get_place_fips_label(code):
	code = int(code)
	switcher = {
		10075: "Broussard",
		12665: "Carencro",
		22255: "Duson",
		40735: "Lafayette",
		99055: "Parishwide",
		68475: "Scott",
		83335: "Youngsville"
	}

	description = switcher.get(code, "")

	return description

def get_mill_type_label(code):
	switcher = {
		"M": "Millage",
		"F": "Flat Fee",
		"A": "Acreage",
		"O": "Overlay/Partial"
	}

	description = switcher.get(code, "")

	return description

def get_ltc_sub_class_code_description(code):
	code = int(code)
	switcher = {
		1000: "Agricultural Lands Class I",
		1050: "Agricultural Lands Class I - Less Than 3 Acres",
		1100: "Agricultural Lands Class II",
		1150: "Agricultural Lands Class II - Less Than 3 Acres",
		1200: "Agricultural Lands Class III",
		1250: "Agricultural Lands Class III - Less Than 3 Acres",
		1265: "Agricultural Lands Class III",
		1300: "Agricultural Lands Class IV",
		1350: "Agricultural Lands Class IV - Less Than 3 Acres",
		1500: "Timberlands Class I",
		1550: "Timberlands Class I - Less Than 3 Acres",
		1600: "Timberlands Class II",
		1650: "Timberlands Class II - Less Than 3 Acres",
		1700: "Timberlands Class III",
		1750: "Timberlands Class III - Less Than 3 Acres",
		1800: "Timberlands Class IV",
		1850: "Timberlands Class IV - Less Than 3 Acres",
		2000: "Fresh Water Marsh",
		2050: "Fresh Water Marsh - Less Than 3 Acres",
		2200: "Brackish Water Marsh",
		2250: "Brackish Water Marsh - Less Than 3 Acres",
		2400: "Salt Water Marsh (Use Value)",
		2450: "Salt Water Marsh (Use Value) - Less Than 3 Acres",
		3000: "Agricultural Acreage",
		3010: "Timber Acreage (Market Value)",
		3020: "Marsh Acreage (Market Value)",
		3022: "Lake Servitude Lands (Market Value)",
		3024: "Batture Land (Market Value)",
		3030: "Commercial Acreage",
		3040: "Industrial Acreage",
		3050: "Institutional Acreage",
		3060: "Residential Acreage",
		3070: "Trailer Parks (Market Value)",
		3200: "Agricultural Acreage",
		3210: "Timber Acreage (Market Value)",
		3220: "Marsh Acreage (Market Value)",
		3222: "Lake Servitude Lands (Market Value)",
		3224: "Batture Land (Market Value)",
		3230: "Commercial Acreage",
		3232: "Golf Course",
		3240: "Industrial Acreage",
		3250: "Institutional Acreage",
		3260: "Residential Acreage",
		3270: "Trailer Parks (Market Value)",
		3400: "Residential Subdivision Lot",
		3410: "Trailer Park",
		3420: "Commercial Subdivision Lot",
		3430: "Industrial Subdivision Lot",
		3440: "Institutional Subdivision Lot",
		3600: "Residential Non-subdivision Lot",
		3610: "Trailer Park",
		3620: "Commercial Non-subdivision Lot",
		3630: "Industrial Non-subdivision Lot",
		3640: "Institutional Non-subdivision Lot",
		3690: "Miscellaneous Land",
		3700: "No Land Value (Leased Property)",
		4000: "Single Family Residence",
		4010: "Manufactured Housing",
		4015: "Modular Homes",
		4020: "Townhouse/duplexes",
		4030: "Urban Row Houses",
		4040: "Multi-family (Apartments)",
		4050: "Clubhouses",
		4060: "Resort Cottages And Cabins",
		4061: "A-frame Cabins",
		4070: "Log And Dome Houses",
		4080: "Tropical Housing (Camps)",
		4090: "Old Residences (Historical)",
		4091: "Prefabricated Cottages",
		4092: "Elevated Homes",
		4095: "Storage Garages And Workshops",
		4099: "Unidentified Residential Improvements",
		4500: "Clubs & Hotels",
		4510: "Motels",
		4520: "Stores & Commercial Buildings",
		4530: "Garages Industrials Lofts & Warehouses",
		4540: "Offices Medical & Public Buildings",
		4550: "Churches Theaters & Auditoriums",
		4560: "Sheds & Farm Buildings",
		4570: "Schools & Classrooms",
        4580: "Short Term Rental",
		4590: "Old Commercial Buildings (Historical)",
		4599: "Unidentified Commercial Improvements",
		5000: "Inventories & Merchandise",
		5100: "Machinery & Equipment",
		5200: "Business Furniture & Fixtures",
		5300: "Computer Hardware/Software",
		5310: "Electronics",
		5320: "Leasehold Improvements",
		5330: "Telecommunications Equipment",
		5340: "Cell Towers",
		5350: "Video Poker Machines",
		5360: "Cable Television",
		5390: "Other",
		5399: "Non-reporting Of Lat",
		5400: "Credits",
		5500: "Leased Equipment",
		5600: "Lease Lines",
		5610: "Gathering Lines",
		5620: "Pipelines Other Than Public Service",
		5700: "Oil & Gas Surface Equipment",
		6000: "Watercraft (On-shore)",
		6100: "Watercraft (Offshore)",
		6200: "Private Aircraft",
		6210: "Commercial Aircraft",
		6400: "Financial Institutions",
		6600: "Drilling Rigs",
		6800: "Oil Wells",
		6801: "Future Utility",
		6802: "Non Future Utility",
		6810: "Gas Wells",
		6811: "Future",
		6812: "Non Future",
		6820: "Injection Wells Service Wells",
		6830: "Commercial Disposal Wells",
		8000: "Aircraft",
		8010: "Ground Equipment",
		8100: "Barge Lines",
		8200: "Lines",
		8202: "Utility Coop-lines",
		8206: "Utility Noncoop-lines",
		8210: "Land",
		8220: "Improvements",
		8230: "Machinery & Equipment",
		8240: "Construction Work In Progress",
		8250: "Other",
		8300: "Lines",
		8310: "Oil & Gas Storage",
		8320: "Machinery & Equipment",
		8330: "Land",
		8340: "Right Of Ways",
		8350: "Open Access",
		8360: "Improvements",
		8370: "Construction Work In Progress",
		8380: "Other",
		8400: "Private Car Lines",
		8500: "Main Lines",
		8510: "Second Lines",
		8520: "Side Lines",
		8530: "Lands",
		8540: "Improvements",
		8550: "Other",
		8560: "Rolling Stock",
		8600: "Lines",
		8610: "Land",
		8620: "Improvements",
		8630: "Machinery & Equipment",
		8640: "Construction Work In Progress",
		8650: "Other"
	}

	description = switcher.get(code, "")

	return description


def get_assessment_type_description(code):
	switcher = {
		"RE": "Real Estate",
		"PP": "Personal Property",
		"PS": "Public Service"
	}

	description = switcher.get(code, "")

	return description


def get_assessment_status_description(code):
	switcher = {
		"AC": "Active",
		"AJ": "Adjudicated",
		"EX": "Exempt/Tax Free",
		"TE": "Ten Year Exemption",
		"RE": "Restoration",
		"OT": "Other"
	}

	description = switcher.get(code, "")

	return description


def get_homestead_exempt_description(code):
	code = int(code)
	switcher = {
		0: "None",
		1: "Homestead exemption",
		2: "100% Disabled Vet Homestead",
		3: "100% Unmarried Surviving Spouse of Active Duty Homestead"
	}

	description = switcher.get(code, "")

	return description


def get_tax_dist_label(code):
	switcher = {
		"01": "Duson",
		"02": "Broussard",
		"03": "Carencro",
		"04": "Lafayette",
		"05": "Scott",
		"06": "Youngsville",
		"07": "Lafayette Downtown",
		"88": "Unincorporated",
	}

	description = switcher.get(code, "")

	return description


def get_freeze_type_description(code):
	code = int(code)
	switcher = {
		0: "None",
		1: "Over 65 Freeze",
		2: "Disabled",
		3: "Disabled Vet Freeze",
		4: "Widow of POW/MIA"
	}

	description = switcher.get(code, "")

	return description


def parcel_to_new_properties():
	try:
		os.mkdir(directory)
		print ("==========================")
	except OSError:
		print ("==========================")
	else:
		print ("==========================")

	file = open('csv/parcel.csv', 'r')
	reader = csv.DictReader(file)
	data = list(reader)

	i = 0
	while i < len(data):
		# if i > 100:
		# 	break

		row = data[i]
		i += 1

		# remove tildes
		for key, value in row.items():
			row[key] = value.strip('~')

		output = OrderedDict()
		output['data'] = OrderedDict()

		# get the parcel number
		property_id = str(row['parcel_no'])
		output['parcel_no'] = property_id
		print(property_id + ' (' + str(i) + '/' + str(len(data)) + ')')

		# get labels
		place_fips_label = get_place_fips_label(row['place_fips'])
		row['place_fips_label'] = place_fips_label

		tax_dist_label = get_tax_dist_label(row['tax_dist'])
		row['tax_dist_label'] = tax_dist_label
		output['tax_district'] = tax_dist_label

		# split the address into bits
		address = normalize_address(row['par_address'])
		address = clean_up_address(address)
		output['address'] = address

		if (address != 'Non-Identified'):
			try:
				address_parsed = usaddress.tag(address)

				if ('Blk ' in address_parsed[0]['StreetName']):
					address_parsed[0]['AddressNumber'] = address_parsed[0]['AddressNumber'] + ' Block'
					address_parsed[0]['StreetName'].replace('Blk ','')

					output['address'] = address_parsed[0]
					output['address_type'] = 'Block'
				else:
					output['address'] = address_parsed[0]
					output['address_type'] = address_parsed[1]

			except:
				print(property_id + ': Address Not Parseable (address_parsed)')
				output['address_type'] = 'Ambiguous'
		else:
			output['address_type'] = 'Ambiguous'

		if (output['address_type'] == 'Street Address'):
			try:
				address_title = usaddress.tag(address, tag_mapping={
					'AddressNumber': 'address_title',
					'AddressNumberPrefix': 'address_title',
					'AddressNumberSuffix': 'address_title',
					'StreetName': 'address_title',
					'StreetNamePreDirectional': 'address_title',
					'StreetNamePreModifier': 'address_title',
					'StreetNamePreType': 'address_title',
					'StreetNamePostDirectional': 'address_title',
					'StreetNamePostModifier': 'address_title',
					'StreetNamePostType': 'address_title',
					'CornerOf': 'address_title',
					'IntersectionSeparator': 'address_title',
					'LandmarkName': 'address_title',
					'USPSBoxGroupID': 'address_title',
					'USPSBoxGroupType': 'address_title',
					'USPSBoxID': 'address_title',
					'USPSBoxType': 'address_title',
					'BuildingName': 'address_title',
					'OccupancyType': 'address_title',
					'OccupancyIdentifier': 'address_title',
					'SubaddressIdentifier': 'address_title',
					'SubaddressType': 'address_title',
				})
				output['title'] = address_title[0]['address_title']
			except:
				print(property_id + ': Address Not Parseable (address_title)')

		# open that json file
		output['data']['parcel'] = row

		try:
			json_file = open(directory + property_id + '.json', 'r')
			print('updating parcel')
			# open an existing json file, probably
		except:
			json_file = open(directory + property_id + '.json', 'w')
			print('new file')
			# create a new json file

		try:
			# loading data from the json file
			json_data = json.loads(json_file.read())
		except:
			# make an empty dictionary if the file was empty
			json_data = {}

		# merge the csv row data with the json data
		json_data.update(output)

		# print(json_data)

		# then write that to the file
		json_file = open(directory + property_id + '.json', 'w')
		json.dump(json_data, json_file, sort_keys=False, indent=2)




def assmt_to_existing_properties():
	try:
		os.mkdir('json')
		print ("==========================")
	except OSError:
		print ("OSError making json dir")
		print ("==========================")
	else:
		print ("==========================")

	file = open('csv/assmt.csv', 'r')
	reader = csv.DictReader(file)
	data = list(reader)

	i = 0
	while i < len(data):
		# if i > 10:
		# 	break

		row = data[i]
		i += 1

		# remove tildes
		for key, value in row.items():
			row[key] = value.strip('~')

		# get assessment info labels
		assessment_type_description = get_assessment_type_description(row['assessment_type'])
		row['assessment_type_description'] = assessment_type_description
		# output['assessment_type'] = assessment_type_description

		assessment_status_description = get_assessment_status_description(row['assessment_status'])
		row['assessment_status_description'] = assessment_status_description
		# output['assessment_status'] = assessment_status_description

		homestead_exempt_description = get_homestead_exempt_description(row['homestead_exempt'])
		row['homestead_exempt_description'] = homestead_exempt_description

		freeze_description = get_freeze_type_description(row['freeze'])
		row['freeze_description'] = freeze_description

		# get the parcel number and open that json file
		property_id = str(row['Parcel_no'])
		print(property_id + ' (' + str(i) + '/' + str(len(data)) + ')')

		try:
			json_file = open(directory + property_id + '.json', 'r')
			print('updating assmt')
			# open an existing json file
		except:
			json_file = open(directory + property_id + '.json', 'w')
			print('new file')
			# create a new json file

		try:
			# loading data from the json file
			json_data = json.loads(json_file.read())
		except:
			# make an empty dictionary if the file was empty
			json_data = {}

		# merge the csv row data with the json data
		json_data['data']['assmt'] = row

		# print(json_data)

		# then write that to the file
		json_file = open(directory + property_id + '.json', 'w')
		json.dump(json_data, json_file, sort_keys=False, indent=2)

def avalue_to_existing_properties():
	file = open('csv/avalue_sorted.csv', 'r')
	reader = csv.DictReader(file)
	data = list(reader)

	i = 0
	while i < len(data):
		# if i > 10:
		# 	break

		row = data[i]
		i += 1

		# remove tildes
		for key, value in row.items():
			row[key] = value.strip('~')

		property_id = str(row['assessment_no'])
		print(property_id + ' (' + str(i) + '/' + str(len(data)) + ')')

		# remove unnecessary data (these are contained elsewhere in the json file)
		del row['fips_code']
		del row['tax_year']

		# clean up LTC code data
		row['Ltc_sub_class_code'] = row['Ltc_sub-class_code']

		Ltc_sub_class_code_description = get_ltc_sub_class_code_description(row['Ltc_sub-class_code'])
		row['Ltc_sub_class_code_description'] = Ltc_sub_class_code_description

		del row['Ltc_sub-class_code']

		# get read to write to .json

		try:
			# open a json file for a property
			json_file = open(directory + property_id + '.json', 'r')
			print('updating avalue')
		except:
			# otherwise toss out a log
			print('file not found')
			continue

		try:
			# loading data from the json file
			json_data = json.loads(json_file.read(), object_pairs_hook=OrderedDict)
		except:
			print('file empty')
			continue

		try:
			values = json_data['data']['values']
			values_count = str(len(values))
			values.update( { values_count : row } )
		except:
			values = OrderedDict.fromkeys({'0'})
			values.update( { '0' : row } )

		# move stuff into a new array to do math and then convert back to string

		json_data['data']['values'] = values

		json_file = open(directory + property_id + '.json', 'w')
		json.dump(json_data, json_file, sort_keys=False, indent=2)

def amillage_to_existing_properties():
	file = open('csv/amillage.csv', 'r')
	reader = csv.DictReader(file)
	data = list(reader)

	i = 0
	while i < len(data):
		# if i > 35:
		# 	break

		row = data[i]
		i += 1

		# remove tildes
		for key, value in row.items():
			row[key] = value.strip('~')

		property_id = str(row['assessment_no'])
		print(property_id + ' (' + str(i) + '/' + str(len(data)) + ')')

		# remove unnecessary data (these are contained elsewhere in the json file)
		del row['fips_code']
		del row['tax_year']
		# del row['assessment_no']

		# get mill type label
		mill_type_label = get_mill_type_label(row['mill_type'])
		row['mill_type_label'] = mill_type_label

		try:
			# open a json file for a property
			json_file = open(directory + property_id + '.json', 'r')
			print('updating amillage')
		except:
			# otherwise toss out a log
			print('file not found')
			continue

		try:
			# loading data from the json files
			json_data = json.loads(json_file.read(), object_pairs_hook=OrderedDict)
		except:
			print('file empty')
			continue

		# pprint.pprint(json_data)

		try:
			millages = json_data['data']['millages']
			millages_count = str(len(millages))
			millages.update( { millages_count : row } )
		except:
			millages = OrderedDict.fromkeys({'0'})
			millages.update( { '0' : row } )

		# pprint.pprint(millages)

		json_data['data']['millages'] = millages

		json_file = open(directory + property_id + '.json', 'w')
		json.dump(json_data, json_file, sort_keys=False, indent=2)

try:
	arg = sys.argv[1]

	if arg == 'all':
		parcel_to_new_properties()
		assmt_to_existing_properties()
		avalue_to_existing_properties()
		amillage_to_existing_properties()
	elif arg == 'parcel':
		parcel_to_new_properties()
	elif arg == 'assmt':
		assmt_to_existing_properties()
	elif arg == 'avalue':
		avalue_to_existing_properties()
	elif arg == 'amillage':
		amillage_to_existing_properties()
except:
	print("no arg, or other error")