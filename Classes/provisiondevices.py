
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

# Azure IoT Libraries
from azure.keyvault.certificates import CertificateClient, CertificatePolicy,CertificateContentType, WellKnownIssuerNames 
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient
from azure.identity import ClientSecretCredential

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

        # Load the Devices Cache File for any devices
        # that have already been provisioned
        devicescache = DevicesCache(self.logger)
        self.logger.info("[DEVICES] devicescache.data Count %s" % str(len(devicescache.data["Devices"])))

        # Make a working copy of the cache file
        self.data = devicescache.data
        self.data["Devices"] = [x for x in devicescache.data["Devices"] if x["DeviceName"] == "Simulated Device"]
        self.logger.info("[DEVICES] self.data Count %s" % str(len(self.data["Devices"])))
        devicescache.load_file()
        self.devices_provision = devicescache.data
        self.devices_provision["Devices"] = [x for x in devicescache.data["Devices"] if x["DeviceName"] != "Simulated Device"]
        self.logger.info("[DEVICES] self.devices_provision.data Count %s" % str(len(self.devices_provision["Devices"])))

        # secrets
        scope_id = None
        device_primary_key = None
        device_secondary_key = None
        gateway_primary_key = None
        gateway_secondary_key = None

        # load the secrets
        secrets = Secrets(self.logger)
        if secrets.data["UseKeyVault"]:
          
          self.logger.info("[USING KEY VAULT SECRETS]")
          
          # key vault account uri
          key_vault_uri = secrets.data["KeyVaultSecrets"]["KeyVaultUri"]
          self.logger.info("[KEY VAULT URI] %s" % key_vault_uri)

          tenant_id = secrets.data["KeyVaultSecrets"]["TenantId"]
          client_id = secrets.data["KeyVaultSecrets"]["ClientId"]
          client_secret = secrets.data["KeyVaultSecrets"]["ClientSecret"]
          
          # Get access to Key Vault Secrets
          credential = ClientSecretCredential(tenant_id, client_id, client_secret)
          self.logger.info("[credential] %s" % credential)
          secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
          self.logger.info("[secret_client] %s" % secret_client)

          # Read all of our Secrets for Accessing IoT Central
          scope_id = secret_client.get_secret(secrets.data["KeyVaultSecrets"]["ScopeId"])
          device_primary_key = secret_client.get_secret(secrets.data["KeyVaultSecrets"]["DeviceConnect"]["SaSKeys"]["Primary"])
          device_secondary_key = secret_client.get_secret(secrets.data["KeyVaultSecrets"]["DeviceConnect"]["SaSKeys"]["Secondary"])
          gateway_primary_key = secret_client.get_secret(secrets.data["KeyVaultSecrets"]["GatewayConnect"]["SaSKeys"]["Primary"])
          gateway_secondary_key = secret_client.get_secret(secrets.data["KeyVaultSecrets"]["GatewayConnect"]["SaSKeys"]["Secondary"])
        
        else:

          # Read all of our LOCAL Secrets for Accessing IoT Central
          self.logger.info("[USING LOCAL SECRETS]")
          scope_id = secrets.data["LocalSecrets"]["ScopeId"]
          device_primary_key = secrets.data["LocalSecrets"]["DeviceConnect"]["SaSKeys"]["Primary"]
          device_secondary_key = secrets.data["LocalSecrets"]["DeviceConnect"]["SaSKeys"]["Secondary"]
          gateway_primary_key = secrets.data["LocalSecrets"]["GatewayConnect"]["SaSKeys"]["Primary"]
          gateway_secondary_key = secrets.data["LocalSecrets"]["GatewayConnect"]["SaSKeys"]["Secondary"]

          # Verbose
          self.logger.info("[SCOPE ID]: %s" % scope_id)
          self.logger.info("[DEVICE PRIMARY KEY]: %s" % device_primary_key)
          self.logger.info("[DEVICE SECONDARY KEY]: %s" % device_secondary_key)
          self.logger.info("[GATEWAY PRIMARY KEY]: %s" % gateway_primary_key)
          self.logger.info("[GATEWAY SECONDARY KEY]: %s" % gateway_secondary_key)

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
          self.logger.info("[DEVICE] %s" % device_capability_model)
           
          # Get a Device Specific Symetric Key
          device_symmetrickey = symmetrickey.compute_derived_symmetric_key(device_capability_model["DeviceName"], device_secondary_key)
          self.logger.info("[SYMETRIC KEY] %s" % device_symmetrickey)

          # Provision the Device
          self.logger.warning("[PROVISIONING] %s" % device_capability_model["DeviceName"])
          
          if not self.whatif:
            
            provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
              provisioning_host=secrets.data["ProvisioningHost"],
              registration_id=device_capability_model["DeviceName"],
              id_scope=scope_id,
              symmetric_key=device_symmetrickey,
              websockets=True
            )

            provisioning_device_client.provisioning_payload = '{"iotcModelId":"%s"}' % (device_capability_model["DeviceCapabilityModelId"])
            registration_result = await provisioning_device_client.register()

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

