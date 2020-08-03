# ==================================================================================
#   File:   config.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    SaS key class for all operations on connections and generation of
#           keys used to connect via DPS and Azure IoT Central
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import json
import logging

class DevicesCache():

    def __init__(self, Log):
        self.logger = Log
        self.load_file()

    def load_file(self):
        with open('devicescache.json') as config_file:
            self.data = json.load(config_file)
            alerts = self.load_alerts()
            self.logger.info(alerts["Alerts"]["DevicesCache"]["Loaded"].format(self.data))

    def update_file(self, data):
        with open('devicescache.json', 'w') as configs_file:
            alerts = self.load_alerts() 
            self.logger.info(alerts["Alerts"]["DevicesCache"]["Updated"].format(self.data))
            configs_file.write(json.dumps(data, indent=2))

    def load_alerts(self):
        with open('alerts.json', 'r') as alerts_file:
            return json.load(alerts_file)