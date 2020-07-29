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
        opc_url = self.config["UrlPattern"].format(id = 199, port = 4840)
        self.logger.info("[URL] OPC Server IP %s" % opc_url)
        opc_server.set_endpoint(opc_url)

      # Our NameSpace
      namespace = self.config["NameSpace"]
      self.logger.info("[NAMESPACE] ID %s" % namespace)
      if not self.whatif:
        id_namespace = await opc_server.register_namespace(namespace)

      # Create our Nodes and Parameters
      for node in self.nodes:
        name = node["Name"]
        self.logger.info("[NODE NAME] %s" % name)
        
        # Add Node and Begin Populating our Address Space
        if not self.whatif:
          node_obj[name] = await opc_server.nodes.objects.add_object(id_namespace, name)
        
        for variable in node["Variables"]:
          variable_name = variable["DisplayName"]
          telemetry_name = variable["TelemetryName"]
          self.logger.info("[VARIABLE DISPLAY NAME] %s" % variable_name)
          self.logger.info("[VARIABLE TELEMETRY NAME] %s" % telemetry_name)
          range_value = variable["RangeValues"][0]
          self.logger.info("[RANGE VALUE] %s" % range_value)
          opc_variant_type = variant_type.map_variant_type(variable["IoTCDataType"])
          self.logger.info("[IoTC DATA TYPE] %s" % variable["IoTCDataType"])
          self.logger.info("[VARIANT DATA TYPE] %s" % opc_variant_type)
          self.logger.info("[DATA TYPE] %s" % opc_variant_type)

          if not self.whatif:
            variable_obj[variable_name] = await node_obj[name].add_variable(id_namespace, telemetry_name, range_value, varianttype=opc_variant_type, datatype=opc_variant_type)
            await variable_obj[variable_name].set_writable()
            #await opc_server.nodes.objects.add_method(ua.NodeId('ServerMethod', 2), ua.QualifiedName('ServerMethod', 2), func, [ua.VariantType.Int64], [ua.VariantType.Int64])
            self.logger.info("[STARTING SERVER] %s" % opc_url)
      
      while True:
        await asyncio.sleep(5)
        for node in self.nodes:
          temp_dict = self.nodes_dict[node["Name"]]
          temp_dict_counter = self.nodes_dict_counter[node["Name"]]
          self.logger.info("[LOOP: TEMP_DICT] %s" % temp_dict)
          self.logger.info("[LOOP: TEMP_DICT_COUNTER] %s" % temp_dict_counter)
          
          for variable in node["Variables"]:
            variable_name = variable["DisplayName"]
            telemetry_name = variable["TelemetryName"]
            sequence_count = temp_dict[telemetry_name]
            count = temp_dict_counter[telemetry_name]
            self.logger.info("[LOOP: NODE NAME] %s" % temp_dict)
            self.logger.info("[LOOP: VARIABLE NAME] %s" % variable_name)
            self.logger.info("[LOOP: TELEMETRY NAME] %s" % telemetry_name)
            self.logger.info("[LOOP: SEQUENCE COUNT] %s" % str(sequence_count))
            self.logger.info("[LOOP: CURRENT COUNT] %s" % str(count))
            if count < sequence_count:
              count += 1
            else:
              count = 1
            
            self.nodes_dict_counter[node["Name"]] = count
            value = variable["RangeValues"][count]
            self.logger.info("[LOOP: TELEMETRY COUNT] %s" % str(count))
            self.logger.info("[LOOP: TELEMETRY VALUE] %s" % str(value))
            await variable_obj[variable_name].write_value(value)
            self.logger.info("[LOOP: VALUE WRITTEN] %s" % str(value))

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
