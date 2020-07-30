# ==================================================================================
#   File:   opcserver.py
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

# opcua
from asyncua import ua, Server
from asyncua.common.methods import uamethod

# our classes
from Classes.config import Config
from Classes.varianttype import VariantType

class OpcServer():
    
    def __init__(self, Log, WhatIf):
      self.logger = Log
      self.whatif = WhatIf
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

      # Data Type Mappings
      variant_type = VariantType(self.logger)

      # OPCUA Server Setup
      if not self.whatif:
        opc_server = Server()
        await opc_server.init()
        opc_url = self.config["UrlPattern"].format(port = 4840)
        self.logger.info("[URL] %s" % opc_url)
        opc_server.set_endpoint(opc_url)

      # Our NameSpace
      namespace = self.config["NameSpace"]
      self.logger.info("[NAMESPACE] %s" % namespace)
      
      if not self.whatif:
        id_namespace = await opc_server.register_namespace(namespace)

      # Create our Nodes and Parameters
      for node in self.nodes:
        name = node["Name"]

        # Add Node and Begin Populating our Address Space
        if not self.whatif:
          node_obj[name] = await opc_server.nodes.objects.add_object(id_namespace, name)
        
        for variable in node["Variables"]:
          variable_name = variable["DisplayName"]
          telemetry_name = variable["TelemetryName"]
          range_value = variable["RangeValues"][0]
          opc_variant_type = variant_type.map_variant_type(variable["IoTCDataType"])
          log_msg = "[SETUP VARIABLE] NODE NAME: {nn} DISPLAY NAME: {dn} TELEMETRY NAME: {tn} RANGE VALUE: {rv} " \
            "IoTC TYPE: {it} OPC VARIANT TYPE {ovt} OPC DATA TYPE {odt}"
          self.logger.info(log_msg.format(nn = name, dn = variable["DisplayName"], vn = variable["TelemetryName"], \
            tn = variable["TelemetryName"], rv = variable["RangeValues"][0], it = variable["IoTCDataType"], \
              ovt = opc_variant_type, odt = opc_variant_type))

          if not self.whatif:
            variable_obj[variable_name] = await node_obj[name].add_variable(id_namespace, \
              telemetry_name, range_value, varianttype=opc_variant_type, datatype=opc_variant_type)
            await variable_obj[variable_name].set_writable()
            self.logger.info("[STARTING SERVER] %s" % opc_url)
      
      if not self.whatif:
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
                  await variable_obj[variable_name].write_value(value)
                  log_msg = "[LOOP] TELEMETRY COUNT: {tc} VALUE WRITTEN: {vw}"
                  self.logger.info(log_msg.format(tc = count, vw = value))

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
