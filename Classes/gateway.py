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

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription.
    The handler forwards updates to it's referenced python object
    """

    def __init__(self, obj):
        self.obj = obj

    def datachange_notification(self, node, val, data):
        # print("Python: New data change event", node, val, data)
        self.obj.value = data.monitored_item.Value.Value.Value #this sets the value in your python object

class Gateway():
    
    def __init__(self, Log, WhatIf):
      self.logger = Log
      self.whatif = WhatIf
      self.config = []
      self.nodes = []
      self.load_config()
      self.map_telemetry = []
      self.load_map_telemetry()

        
    # -------------------------------------------------------------------------------
    #   Function:   start
    #   Usage:      The start function loads configuration and starts the OPC Server
    # -------------------------------------------------------------------------------
    async def start(self):
      
      # Gateway Loop
      try:

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
              for variable in node["Variables"]:
                read_node = client.get_node(variable["NodeId"])
                val = await read_node.get_value()
                log_msg = "[TELEMETRY] NAME: {tn} VALUE: {val} NODE ID: {ni} DISPLAY NAME: {dn}"
                self.logger.info(log_msg.format(tn = variable["TelemetryName"], val = val, ni = variable["NodeId"], dn = variable["DisplayName"]))

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in Gateway" )
        return
        
      finally:
          await client.disconnect()
    
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


