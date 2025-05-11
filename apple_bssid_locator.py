#!/usr/bin/env -S uv run --script
# -*- coding: utf-8 -*-

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
	parser.add_argument("-a", "--all", help="shows all results returned, not just the requested one", action='store_true')
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
	apple_wloc = AppleWLoc_pb2.AppleWLoc()
	wifi_device = apple_wloc.wifi_devices.add()
	wifi_device.bssid = bssid
	apple_wloc.unknown_value1 = 0
	apple_wloc.return_single_result = 1
	serialized_apple_wloc = apple_wloc.SerializeToString()
	length_serialized_apple_wloc = len(serialized_apple_wloc)
	# Latest versions of the UA string are at https://user-agents.net/applications/cfnetwork/platforms/ios
	headers = {'User-Agent':'locationd/1753.17 CFNetwork/889.9 Darwin/17.2.0'}
	data = b"\x00\x01\x00\x05"+b"en_US"+b"\x00\x13"+b"com.apple.locationd"+b"\x00\x0a"+b"8.1.12B411"+b"\x00\x00\x00\x01\x00\x00\x00" + bytes((length_serialized_apple_wloc,)) + serialized_apple_wloc;
	r = requests.post('https://gs-loc.apple.com/clls/wloc', headers=headers, data=data) # CN of cert on this hostname is sometimes *.ls.apple.com / ls.apple.com, so have to disable SSL verify
	apple_wloc = AppleWLoc_pb2.AppleWLoc()
	apple_wloc.ParseFromString(r.content[10:])
	return process_result(apple_wloc)

def main():
	args = parse_arguments()
	#requests.packages.urllib3.disable_warnings()
	print("Searching for location of bssid: %s" % args.bssid)
	results = query_bssid(args.bssid)

	# Determine which BSSIDs to process
	bssids_to_process = results.keys() if args.all else [args.bssid.lower()]

	found = False
	for bssid in bssids_to_process:
		if bssid in results:
			lat, lon = results[bssid]
			if lat == -180.0 and lon == -180.0:
				continue  # Skip entries that were not found
			lat_str = str(lat)
			lon_str = str(lon)
			if found: print()
			print(f"BSSID: {bssid}")
			print(f"Latitude: {lat_str}")
			print(f"Longitude: {lon_str}")
			if args.map:
				url = f"http://www.google.com/maps/place/{lat_str},{lon_str}"
				webbrowser.open(url)
			found = True

	if not found:
		print("The bssid was not found.")

if __name__ == '__main__':
    main()
