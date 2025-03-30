# -*- coding: utf-8 -*-
#!/usr/bin/python

# Implementation based on https://github.com/hubert3/iSniff-GPS which in turn is based on work from the paper by François-Xavier Aguessy and Côme Demoustier (http://fxaguessy.fr/rapport-pfe-interception-ssl-analyse-donnees-localisation-smartphones/)
# Usage: apple_bssid_locator.py 34:DB:FD:43:E3:A1 --map

import argparse
import sys
import code
import requests
import webbrowser
import AppleWLoc_pb2

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("bssid", type=str, help="display the location of the bssid")
	parser.add_argument("-m", "--map", help="shows the location on google maps", action='store_true')
	args = parser.parse_args()
	return args

def format_bssid(bssid):
	return ':'.join(e.rjust(2, '0') for e in bssid.split(':'))

def process_result(apple_wloc):
	device_locations = {}
	for wifi_device in apple_wloc.wifi_devices:
		if wifi_device.HasField('location'):
			lat = wifi_device.location.latitude * 1e-8
			lon = wifi_device.location.longitude * 1e-8
			mac = format_bssid(wifi_device.bssid)
			device_locations[mac] = (lat,lon)
	return device_locations

def query_bssid(bssid):
	apple_wloc = AppleWLoc_pb2.AppleWLoc(unknown_value1=0, return_single_result=1,
		wifi_devices=[AppleWLoc_pb2.WifiDevice(bssid = bssid)])
	serialized_apple_wloc = apple_wloc.SerializeToString()

	# Latest versions of the UA string are at https://user-agents.net/applications/cfnetwork/platforms/ios
	headers = {'User-Agent':'locationd/1753.17 CFNetwork/889.9 Darwin/17.2.0'}

	# The version string here appears to encode ${APPLE_OS_VERSION}.${APPLE_OS_BUILD},
	# where the "build" strings are typically alphanumeric, e.g. https://en.wikipedia.org/wiki/IOS_18#Release_history
	locale, dotted_class, version = b"en_US", b"com.apple.locationd", b"18.1.1.22B91"

	# .to_bytes default is network/big-endian byte order
	data = (
		(1).to_bytes(2) +
		len(locale).to_bytes(2) + locale +
		len(dotted_class).to_bytes(2) + dotted_class +
		len(version).to_bytes(2) + version +
		(1).to_bytes(4) +
		len(serialized_apple_wloc).to_bytes(4) + serialized_apple_wloc
	)
	r = requests.post('https://gs-loc.apple.com/clls/wloc', headers=headers, data=data, verify=False) # CN of cert on this hostname is sometimes *.ls.apple.com / ls.apple.com, so have to disable SSL verify
	assert r.content[:6] == (1).to_bytes(2) + (1).to_bytes(4), "Pre-protobuf header in response is not what we expected"
	assert r.content[6:10] == (len(r.content) - 10).to_bytes(4), "Pre-protobuf length field in response does not match expected length"
	apple_wloc = AppleWLoc_pb2.AppleWLoc.FromString(r.content[10:])
	return process_result(apple_wloc)

def main():
	args = parse_arguments()
	#requests.packages.urllib3.disable_warnings()
	print("Searching for location of bssid: %s" % args.bssid)
	results = query_bssid(args.bssid)
	lat = "-180.0"
	lon = "-180.0"
	if len(results) > 0:
		location = results[args.bssid.lower()]
		lat = str(location[0])
		lon = str(location[1])
	if lat != "-180.0" or lon != "-180.0":
		print("Latitude: %s" % lat)
		print("Longitude: %s" % lon)
		if args.map == True:
			url = "http://www.google.com/maps/place/" + lat + "," + lon
			webbrowser.open(url)
	else:
		print("The bssid was not found.")

if __name__ == '__main__':
    main()
