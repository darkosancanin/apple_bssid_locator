### Overview 
Simple python tool which finds the location of a wifi access point from its BSSID (Basic Service Set Identifier) which is the MAC address of the wifi access point and optionally displays the location on Google Maps. This is implemented by calling the Apple Location Services API.

### Instructions/Usage
Install python dependencies by running `pip install -r requirements.txt`.

To find the location of a bssid run the following `python apple_bssid_locator.py 34:DB:FD:43:E3:A1`.

To find the location and display it on a map run the following `python apple_bssid_locator.py 34:DB:FD:43:E3:A1 --map`.

### Credits
The implementation is based on https://github.com/hubert3/iSniff-GPS which in turn is based on work from the paper by François-Xavier Aguessy and Côme Demoustier (http://fxaguessy.fr/rapport-pfe-interception-ssl-analyse-donnees-localisation-smartphones/)

### Screenshots
![Console](https://raw.githubusercontent.com/darkosancanin/apple_bssid_locator/master/images/console_screenshot.png)

![Map](https://raw.githubusercontent.com/darkosancanin/apple_bssid_locator/master/images/map_screenshot.png)