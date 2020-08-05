# ==================================================================================
#   File:   gateway.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Gateway acts a Client to the OPC Server and Handles Protocol
#           translation to Azure IoT Central
#
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import json, sys, time, string, threading, asyncio, os, copy
import logging

# For dumping and Loading Address Space option
from pathlib import Path

# opcua
from asyncua import Client, Node, ua

# uses the Azure IoT Device SDK for Python (Native Python libraries)
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from azure.iot.device import MethodResponse

# our classes
from Classes.config import Config
from Classes.maptelemetry import MapTelemetry
from Classes.varianttype import VariantType
from Classes.deviceclient import DeviceClient
from Classes.devicescache import DevicesCache

class Gateway():
    
    def __init__(self, Log, WhatIf):
      self.logger = Log
      self.whatif = WhatIf

      # load up configuration and mapping files
      self.config = []
      self.nodes = []
      self.load_config()

      # Device Information
      self.devices_cache = []
      self.load_devices_cache()

      # Map Telemetry
      self.map_telemetry = []
      self.load_map_telemetry()
      self.telemetry_msg = {}
      self.telemetry_dict = {}

      # Azure Device
      self.device_client = None

    # -------------------------------------------------------------------------------
    #   Function:   start
    #   Usage:      The start function loads configuration and starts the OPC Server
    # -------------------------------------------------------------------------------
    async def start(self):

      # Gateway Loop
      try:
        
        device_client = DeviceClient(self.logger, self.devices_cache["DefaultDeviceName"])
        await device_client.connect()
        self.logger.info("[CONNECTING IOT CENTRAL] %s" % self.device_client)

        # configure the endpoint
        url = self.config["ClientUrlPattern"].format(port = self.config["Port"])
        self.logger.info("[SEEKING ENDPOINT] %s" % url)

        async with Client(url=url) as client:
          
          name_space_index = await client.get_namespace_index(self.map_telemetry["NameSpace"])
          self.logger.info("[NAMESPACE NAME] %s" % self.map_telemetry["NameSpace"])
          self.logger.info("[NAMESPACE INDEX] %s" % name_space_index)
          self.logger.info("[PREPARING TO READ TELEMETRY IN SECONDS] %s" % self.config["ClientFrequencyInSeconds"])

          while True:
            await asyncio.sleep(self.config["ClientFrequencyInSeconds"])

            for node in self.map_telemetry["Nodes"]:
              self.logger.info("[NODE NAME] %s" % node["Name"])
              self.telemetry_dict = {}
              for variable in node["Variables"]:
                read_node = client.get_node(variable["NodeId"])
                val = await read_node.get_value()
                log_msg = "[TELEMETRY] NAME: {tn} VALUE: {val} NODE ID: {ni} DISPLAY NAME: {dn}"
                self.logger.info(log_msg.format(tn = variable["TelemetryName"], val = val, ni = variable["NodeId"], dn = variable["DisplayName"]))
                self.telemetry_dict[variable["TelemetryName"]] = val
                self.logger.info("[DICTIONARY] %s" % self.telemetry_dict)

              await device_client.send_telemetry(self.telemetry_dict, node["InterfacelId"], node["InterfaceInstanceName"])

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in Gateway" )
        return
        
      finally:
          await client.disconnect()
          self.device_client = None
          device_client.disconnect()
    
      return

    # -------------------------------------------------------------------------------
    #   Function:   load_config
    #   Usage:      Loads the configuration from file and setup iterators for
    #               sending telemetry in sequence
    # -------------------------------------------------------------------------------
    def load_config(self):
      
      # Load all the configuration
      config = Config(self.logger)
      self.config = config.data
      self.nodes = self.config["Nodes"]
      return
    
    # -------------------------------------------------------------------------------
    #   Function:   load_map_telemetry
    #   Usage:      Loads the Map Telemetry File that Maps Telemtry for Azure
    #               Iot Central to the Node Id's for the Opc Server.
    # -------------------------------------------------------------------------------
    def load_map_telemetry(self):
      
      # Load all the map
      map_telemetry = MapTelemetry(self.logger)
      map_telemetry.load_file()
      self.map_telemetry = map_telemetry.data
      return

    # -------------------------------------------------------------------------------
    #   Function:   load_devices_cache
    #   Usage:      Loads the Device Cache Information and Configuration
    # -------------------------------------------------------------------------------
    def load_devices_cache(self):
      
      # Load Device Cache
      devices_cache = DevicesCache(self.logger)
      self.devices_cache = devices_cache.data
      return

      

