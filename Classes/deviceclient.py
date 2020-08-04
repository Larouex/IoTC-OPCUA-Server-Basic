# ==================================================================================
#   File:   deviceclient.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Created and send telemetry to Azure IoT Central with this persisted
#           device client
#
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import json, sys, time, string, threading, asyncio, os, copy
import logging

# uses the Azure IoT Device SDK for Python (Native Python libraries)
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from azure.iot.device import MethodResponse

# our classes
from Classes.config import Config
from Classes.maptelemetry import MapTelemetry
from Classes.secrets import Secrets
from Classes.varianttype import VariantType

class DeviceClient():
    
    def __init__(self, Log, ConfigData, MapTelemetryData):
      self.logger = Log
      self.config = ConfigData
      self.map_telemetry = MapTelemetryData
      
      # Azure Device
      self.device_client = None

    # -------------------------------------------------------------------------------
    #   Function:   start
    #   Usage:      The start function creates the device instance
    # -------------------------------------------------------------------------------
    async def start(self):

      try:
        self.device_client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=dps_cache[0],
            hostname=dps_cache[1],
            device_id=dps_cache[2],
            websockets=use_websockets
        )
