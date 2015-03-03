# -*- coding: utf-8 -*-
#!/usr/bin/python
# Based on https://github.com/hubert3/iSniff-GPS

import sys
import code
import requests
import webbrowser
import AppleWLoc_pb2

def format_bssid(bssid):
	result = ''
	for e in bssid.split(':'):
		if len(e) == 1:
			e='0%s'%e
		result += e+':'
	return result.strip(':')

def process_result(apple_wloc):
	device_locations = {}
	for wifi_device in apple_wloc.wifi_devices:
		if wifi_device.HasField('location'):
			lat = wifi_device.location.latitude * pow(10,-8)
			lon = wifi_device.location.longitude * pow(10,-8)
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
	headers = {'Content-Type':'application/x-www-form-urlencoded', 'Accept':'*/*', "Accept-Charset": "utf-8","Accept-Encoding": "gzip, deflate",\
			"Accept-Language":"en-us", 'User-Agent':'locationd/1753.17 CFNetwork/711.1.12 Darwin/14.0.0'}
	data = "\x00\x01\x00\x05"+"en_US"+"\x00\x13"+"com.apple.locationd"+"\x00\x0a"+"8.1.12B411"+"\x00\x00\x00\x01\x00\x00\x00" + chr(length_serialized_apple_wloc) + serialized_apple_wloc;
	r = requests.post('https://gs-loc.apple.com/clls/wloc', headers=headers, data=data, verify=False) # CN of cert on this hostname is sometimes *.ls.apple.com / ls.apple.com, so have to disable SSL verify
	apple_wloc = AppleWLoc_pb2.AppleWLoc() 
	apple_wloc.ParseFromString(r.content[10:])
	return process_result(apple_wloc)

def main():
	requests.packages.urllib3.disable_warnings()
	bssid = '20:E5:2a:fb:c0:5e'
	results = query_bssid(bssid)
	location = results[bssid.lower()]
	lat = location[0]
	lon = location[1]
	print lat
	print lon
	#print results
	url = "http://www.google.com/maps/place/" + str(location[0]) + "," + str(location[1])
	#webbrowser.open(url)

if __name__ == '__main__':
    main()