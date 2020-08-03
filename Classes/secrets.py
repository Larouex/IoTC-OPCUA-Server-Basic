# ==================================================================================
#   File:   secrets.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Loads the secrets file
#
#   Online: www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import json
import logging

class Secrets():

    def __init__(self, Log):
        self.logger = Log
        self.load_file()

    def load_file(self):
        with open('secrets.json', 'r') as config_file:
            self.data = json.load(config_file)
            alerts = self.load_alerts()
            self.logger.info(alerts["Alerts"]["Secrets"]["Loaded"].format(self.data))

    def load_alerts(self):
        with open('alerts.json', 'r') as alerts_file:
            return json.load(alerts_file)
