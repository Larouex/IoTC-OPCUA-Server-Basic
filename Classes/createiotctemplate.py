# ==================================================================================
#   File:   createiotctemplate.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Loads the Config and Generates a Device Template for use with Azure
#           IoT Central
#
#   Online: www.hackinmakin.com
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
from Classes.dcmtemplate import DcmTemplate
from Classes.varianttype import VariantType

class CreateIoTCTemplate():
    
    def __init__(self, Log):
      self.logger = Log
      self.config = []
      self.dcm_template = None
      self.dcm_template_data = []
      self.nodes = []
      self.load_config()
      self.load_dcm_template()
        
    # -------------------------------------------------------------------------------
    #   Function:   create
    #   Usage:      The start function loads configuration and starts the OPC Server
    # -------------------------------------------------------------------------------
    async def create(self, fileName):

      self.prep_dcm()
      
      # Create our Nodes and Parameters
      for node in self.nodes:
        interface = self.create_interface(node["InterfaceInstanceName"], node["InterfacelId"], node["Name"])
        self.logger.info("[INTERFACE] %s" % interface)
        
        for variable in node["Variables"]:
            telemetry = self.create_telemetry(variable["DisplayName"], variable["TelemetryName"], variable["IoTCDataType"])
            self.logger.info("[TELEMETRY] %s" % telemetry)
            interface["schema"]["contents"].append(telemetry)
        
        self.dcm_template_data["implements"].append(interface)
      
      # Write the file to the ./DeviceTemplates folder
      if fileName == None:
        fileName = self.config["NameSpace"] + ".json"
      self.dcm_template.update_file(fileName, self.dcm_template_data)
      self.logger.info("[DCM] %s" % self.dcm_template_data)

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
    #   Function:   load_dcm_template
    #   Usage:      Loads the dcm template for generatig a new DCM file
    # -------------------------------------------------------------------------------
    def load_dcm_template(self):
      
      # Load the template file
      self.dcm_template = DcmTemplate(self.logger)
      self.dcm_template_data = self.dcm_template.data

    def prep_dcm(self):
      self.dcm_template_data["@id"] = self.dcm_template_data["@id"].format(id = self.config["DeviceCapabilityModelId"])
      self.dcm_template_data["displayName"] = self.dcm_template_data["displayName"].format(displayName = self.config["ServerDiscoveryName"])
      self.dcm_template_data["description"] = self.dcm_template_data["description"].format(description = self.config["Description"])


    def create_interface(self, name, id, displayName):
      newInterface = {
        "@type": "InterfaceInstance",
        "name": name, 
        "schema": {
          "@id": id,
          "@type": "Interface",
          "displayName": displayName,
          "contents": [
          ]
        }
      }
      return newInterface 
    
    def create_telemetry(self, displayName, telemetryName, schema):
      newTelemetry = {
        "@type": "Telemetry",
        "displayName": {
          "en": displayName
        },
        "name": telemetryName,
        "schema": schema
      }
      return newTelemetry 
