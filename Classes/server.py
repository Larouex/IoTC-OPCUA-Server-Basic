# ==================================================================================
#   File:   server.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    This is the class that handles config and creation of the OPC Server
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
from asyncua import ua, Server
from asyncua.common.methods import uamethod

# our classes
from Classes.config import Config
from Classes.varianttype import VariantType

class Server():
    
    def __init__(self, Log, WhatIf, CacheAddrSpace):
      self.logger = Log
      self.whatif = WhatIf
      self.cache_addr_space = CacheAddrSpace
      self.config = []
      self.nodes = []
      self.nodes_dict = {}
      self.nodes_dict_counter = {}
      self.load_config()
        
    # -------------------------------------------------------------------------------
    #   Function:   start
    #   Usage:      The start function loads configuration and starts the OPC Server
    # -------------------------------------------------------------------------------
    async def start(self):

      node_obj = {}
      variable_obj = {}

      # Data Type Mappings (OPCUA Datatypes to IoT Central Datatypes)
      variant_type = VariantType(self.logger)
      
      # OPCUA Server Setup
      # Here we setup the Server and add discovery
      try:

        # configure the endpoint
        opc_url = self.config["UrlPattern"].format(ip ="0.0.0.0", port = 4840)
        
        if not self.whatif:
          
          # init the server
          opc_server = Server()
          await opc_server.init()
          
          # set the endpoint
          opc_server.set_endpoint(opc_url)
          
          # set discovery
          opc_server.set_application_uri(self.config["ApplicationUri"])
          opc_server.set_server_name(self.config["ServerDiscoveryName"])

        log_msg = "[SERVER CONFIG] ENDPOINT: {ep} APPLICATION URI: {au} APPLICATION NAME: {an}"
        self.logger.info(log_msg.format(ep = opc_url, au = self.config["ApplicationUri"], an = self.config["ServerDiscoveryName"]))

      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in OPCUA Server Setup" )
        return

      # OPCUA Server Setup Nodes
      # Here we setup the Nodes and Variables
      try:

        # Set NameSpace
        namespace = self.config["NameSpace"]
        self.logger.info("[NAMESPACE] %s" % namespace)
        
        if not self.whatif:
          id_namespace = await opc_server.register_namespace(namespace)

        # Create our Nodes and Parameters
        for node in self.nodes:

          # Add Node and Begin Populating our Address Space
          if not self.whatif:
            node_obj[node["Name"]] = await opc_server.nodes.objects.add_object(id_namespace, node["Name"])
          
          for variable in node["Variables"]:
            variable_name = variable["DisplayName"]
            telemetry_name = variable["TelemetryName"]
            range_value = variable["RangeValues"][0]
            opc_variant_type = variant_type.map_variant_type(variable["IoTCDataType"])
            log_msg = "[SETUP VARIABLE] NODE NAME: {nn} DISPLAY NAME: {dn} TELEMETRY NAME: {tn} RANGE VALUE: {rv} " \
              "IoTC TYPE: {it} OPC VARIANT TYPE {ovt} OPC DATA TYPE {odt}"
            self.logger.info(log_msg.format(nn = node["Name"], dn = variable["DisplayName"], vn = variable["TelemetryName"], \
              tn = variable["TelemetryName"], rv = variable["RangeValues"][0], it = variable["IoTCDataType"], \
                ovt = opc_variant_type, odt = opc_variant_type))

            if not self.whatif:
              variable_obj[telemetry_name] = await node_obj[node["Name"]].add_variable(id_namespace, telemetry_name, range_value)
              await variable_obj[telemetry_name].set_writable()
      
      except Exception as ex:
        self.logger.error("[ERROR] %s" % ex)
        self.logger.error("[TERMINATING] We encountered an error in OPCUA Server Setup for the Nodes and Variables" )
        return
      
      # Start the server and save the address space
      try:
        
        if not self.whatif and self.cache_addr_space == "save":
          filename = Path(self.config["CacheAddrSpaceFileName"])
          opc_server.start()
          opc_server.iserver.dump_address_space(filename)
          opc_server.stop()
          self.logger.info("[CACHE ADDRESS SPACE] Saved and Server Terminated. Now run with -c load")
          return

      except Exception as ex:
          self.logger.error("[ERROR] %s" % ex)
          self.logger.error("[TERMINATING] We encountered an error in OPCUA Server Setup for the Nodes and Variables" )
          return

      # We start the server loop if we are not in WhatIf and the CacheAddrSpace
      # is null (not set) or load. If it was load, we pulled it from the cache on
      # server init()...
      if not self.whatif and (self.cache_addr_space == None or self.cache_addr_space == "load"):
        
        self.logger.info("[STARTING SERVER] %s" % opc_url)
        
        if self.cache_addr_space == "load":
          filename = Path(self.config["CacheAddrSpaceFileName"])
          opc_server.iserver.load_address_space(filename)
          self.logger.info("[CACHE ADDRESS SPACE] Loaded Address Space Cache from %s" % filename)

        opc_server.start()

        async with opc_server:
          while True:
            await asyncio.sleep(5)
            for node in self.nodes:
              temp_dict = self.nodes_dict[node["Name"]]
              temp_dict_counter = self.nodes_dict_counter[node["Name"]]
              
              for variable in node["Variables"]:
                count = temp_dict_counter[variable["TelemetryName"]]
                sequence_count = temp_dict[variable["TelemetryName"]]
                log_msg = "[LOOP] NODE NAME: {nn} DISPLAY NAME: {vn} TELEMETRY NAME: {tn} SEQUENCE COUNT: {sc} CURRENT COUNT {cc}"
                self.logger.info(log_msg.format(nn = node["Name"], vn = variable["DisplayName"], tn = variable["TelemetryName"], sc = temp_dict[variable["TelemetryName"]], cc = temp_dict_counter[variable["TelemetryName"]]))

                if count > (sequence_count - 1):
                  count = 0              

                # Choose the next value in the telemetry sequence for the variable
                self.nodes_dict_counter[node["Name"]][variable["TelemetryName"]] = (count + 1)
                value = variable["RangeValues"][count]
                
                if not self.whatif:
                  current_value = await variable_obj[variable["TelemetryName"]].get_value()
                  await variable_obj[variable["TelemetryName"]].write_value(value)
                  log_msg = "[LOOP] TELEMETRY COUNT: {tc} CURRENT VALUE: {cv} NEW VALUE WRITTEN: {vw}"
                  self.logger.info(log_msg.format(tc = count, cv = current_value, vw = value))

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
      
      # These counters support looping through our bounded telemetry values
      for node in self.nodes:
        variable_dict = {}
        variable_dict_counter = {}
        for variable in node["Variables"]:
          variable_dict[variable["TelemetryName"]] = len(variable["RangeValues"])
          variable_dict_counter[variable["TelemetryName"]] = 1

        self.nodes_dict[node["Name"]] = copy.deepcopy(variable_dict)
        self.nodes_dict_counter[node["Name"]] = copy.copy(variable_dict_counter)
      
      self.logger.info("[NODES_DICT] %s" % self.nodes_dict)
      self.logger.info("[NODES_DICT_COUNTER] %s" % self.nodes_dict_counter)
