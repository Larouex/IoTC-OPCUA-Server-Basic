
# ==================================================================================
#   File:   provisiondevices.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Provisions Devices and updates cache file and do device provisioning 
#           via DPS for IoT Central
#
#   Online: www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import time, logging, string, json, os, binascii, struct, threading, asyncio, datetime

# Sur classes
from Classes.devicescache import DevicesCache
from Classes.secrets import Secrets
from Classes.symmetrickey import SymmetricKey
from Classes.config import Config


# uses the Azure IoT Device SDK for Python (Native Python libraries)
from azure.iot.device.aio import ProvisioningDeviceClient

# -------------------------------------------------------------------------------
#   ProvisionDevices Class
# -------------------------------------------------------------------------------
class ProvisionDevices():

    timer = None
    timer_ran = False
    dcm_value = None

    def __init__(self, Log, WhatIf, Id):
        self.logger = Log
        self.whatif = WhatIf
        self.iddevice = Id
        self.config = {}
        self.nodes = {}
        self.data = []
        self.devices_provision = []
        self.new_devices = []
        self.characteristics = []
        self.load_config()
  
    async def provision_devices(self):

        # Make a working copy of the cache file
        devicescache = DevicesCache(self.logger)
        self.data = devicescache.data
        self.data["Devices"] = [x for x in devicescache.data["Devices"] if x["DeviceName"] == "Simulated Device"]
        self.logger.info("[DEVICES] self.data Count %s" % len(self.data["Devices"]))

        # load the secrets
        secrets = Secrets(self.logger)
        secrets.init()

        # Symetric Key for handling Device Specific SaS Keys
        symmetrickey = SymmetricKey(self.logger)

        try:

          # Gather the DCM Information
          device_id = self.config["DeviceName"].format(id=self.iddevice)
          dcm_id = self.config["DeviceCapabilityModelId"]
          device_capability_model = self.create_device_capability_model(device_id, dcm_id)
          self.logger.info("[DCM ID] %s" % dcm_id)
          self.logger.info("[DEVICE ID] %s" % device_id)
          self.logger.info("[DCM] %s" % device_capability_model)

          # Let's Look at the Config File and Generate 
          # our Device from the OPC Server Configuration
          for node in self.nodes:
            device_interface = self.create_device_interface(node["Name"], node["InterfacelId"], node["InterfaceInstanceName"])
            device_capability_model["Interfaces"].append(device_interface)
            self.logger.info("[INTERFACE] %s" % device_interface)

          # Dump the Device Info  
          self.logger.info("[DEVICE] MODEL %s" % device_capability_model)
           
          # Get a Device Specific Symetric Key
          device_symmetrickey = symmetrickey.compute_derived_symmetric_key(device_capability_model["DeviceName"], secrets.get_device_secondary_key())
          self.logger.info("[SYMETRIC KEY] %s" % device_symmetrickey)

          # Provision the Device
          self.logger.info("[PROVISIONING] %s" % device_capability_model["DeviceName"])
          
          if not self.whatif:
            
            self.logger.info("[PROVISIONING HOST]: %s" % secrets.get_provisioning_host())

            provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
              provisioning_host = secrets.get_provisioning_host(),
              registration_id = device_capability_model["DeviceName"],
              id_scope = secrets.get_scope_id(),
              symmetric_key = device_symmetrickey,
              websockets=True
            )

            provisioning_device_client.provisioning_payload = '{"iotcModelId":"%s"}' % (device_capability_model["DeviceCapabilityModelId"])
            registration_result = await provisioning_device_client.register()
            device_capability_model["AssignedHub"] = registration_result.registration_state.assigned_hub
            device_capability_model["DeviceSymmetricKey"] = device_symmetrickey
            self.logger.info("[REGISTRATION RESULT] %s" % registration_result)

          self.data["Devices"].append(device_capability_model)

        except Exception as ex:
          self.logger.error("[ERROR] %s" % ex)
          self.logger.error("[TERMINATING] We encountered an error provisioning device for OPC Server" )
          return

        # Update the Cache
        #if not self.whatif:
        devicescache.update_file(self.data)

        return

    # -------------------------------------------------------------------------------
    #   Function:   load_config
    #   Usage:      Loads the configuration
    # -------------------------------------------------------------------------------
    def load_config(self):
      
      # Load all the configuration
      config = Config(self.logger)
      self.config = config.data
      self.nodes = self.config["Nodes"]

    # -------------------------------------------------------------------------------
    #   Function:   create_device_interface
    #   Usage:      Returns a Device Interface for Interfaces Array
    # -------------------------------------------------------------------------------
    def create_device_capability_model(self, deviceName, id):
      newDeviceCapabilityModel = {
        "DeviceName": deviceName, 
        "AssignedHub": "iot-hub-connection",
        "DeviceSymmetricKey": "device-symetric-key",
        "DeviceCapabilityModelId": id,
        "Interfaces": [
        ],
        "LastProvisioned": str(datetime.datetime.now())
      } 
      return newDeviceCapabilityModel 

    # -------------------------------------------------------------------------------
    #   Function:   create_device_interface
    #   Usage:      Returns a Device Interface for Interfaces Array
    # -------------------------------------------------------------------------------
    def create_device_interface(self, name, id, instantName):
      newInterface = {
        "Name": name,
        "InterfacelId": id,
        "InterfaceInstanceName": instantName
      }
      return newInterface 

