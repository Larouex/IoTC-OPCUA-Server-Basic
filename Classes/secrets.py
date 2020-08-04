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
import time, logging, string, json, os, binascii, struct, threading, asyncio, datetime

# Azure IoT Libraries
from azure.keyvault.certificates import CertificateClient, CertificatePolicy,CertificateContentType, WellKnownIssuerNames 
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient
from azure.identity import ClientSecretCredential

class Secrets():

    def __init__(self, Log):
      # load file
      self.logger = Log
      self.data = []
      self.load_file()      

      # creds
      self.credential = None
      self.secret_client = None

      # values to access
      self.provisioning_host = None
      self.scope_id = None
      self.device_primary_key = None
      self.device_secondary_key = None
      self.gateway_primary_key = None
      self.gateway_secondary_key = None

    def load_file(self):
      with open('secrets.json', 'r') as config_file:
        self.data = json.load(config_file)
        alerts = self.load_alerts()
        self.logger.debug(alerts["Alerts"]["Secrets"]["Loaded"].format(self.data))

    def load_alerts(self):
      with open('alerts.json', 'r') as alerts_file:
        return json.load(alerts_file)

    def update_device_secrets(self, data):
        with open('secrets.json', 'w') as configs_file:
            alerts = self.load_alerts() 
            self.logger.info(alerts["Alerts"]["Secrets"]["Updated"].format(self.data))
            self.data["Devices"] = data
            configs_file.write(json.dumps(self.data, indent=2))

    def init(self):

      self.provisioning_host = self.data["ProvisioningHost"]

      if self.data["UseKeyVault"]:
        
        self.logger.info("[USING KEY VAULT SECRETS]")
          
        # key vault account uri
        key_vault_uri = self.data["KeyVaultSecrets"]["KeyVaultUri"]
        self.logger.debug("[KEY VAULT URI] %s" % key_vault_uri)

        tenant_id = self.data["KeyVaultSecrets"]["TenantId"]
        client_id = self.data["KeyVaultSecrets"]["ClientId"]
        client_secret = self.data["KeyVaultSecrets"]["ClientSecret"]
          
        # Get access to Key Vault Secrets
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

        self.logger.debug("[credential] %s" % credential)
        self.logger.debug("[secret_client] %s" % secret_client)

        # Read all of our Secrets for Accessing IoT Central
        self.scope_id = self.secret_client.get_secret(self.data["KeyVaultSecrets"]["ScopeId"])
        self.device_primary_key = self.secret_client.get_secret(self.data["KeyVaultSecrets"]["DeviceConnect"]["SaSKeys"]["Primary"])
        self.device_secondary_key = self.secret_client.get_secret(self.data["KeyVaultSecrets"]["DeviceConnect"]["SaSKeys"]["Secondary"])
        self.gateway_primary_key = self.secret_client.get_secret(self.data["KeyVaultSecrets"]["GatewayConnect"]["SaSKeys"]["Primary"])
        self.gateway_secondary_key = self.secret_client.get_secret(self.data["KeyVaultSecrets"]["GatewayConnect"]["SaSKeys"]["Secondary"])
        
      else:

        # Read all of our LOCAL Secrets for Accessing IoT Central
        self.logger.info("[USING LOCAL SECRETS]")
        self.scope_id = self.data["LocalSecrets"]["ScopeId"]
        self.device_primary_key = self.data["LocalSecrets"]["DeviceConnect"]["SaSKeys"]["Primary"]
        self.device_secondary_key = self.data["LocalSecrets"]["DeviceConnect"]["SaSKeys"]["Secondary"]
        self.gateway_primary_key = self.data["LocalSecrets"]["GatewayConnect"]["SaSKeys"]["Primary"]
        self.gateway_secondary_key = self.data["LocalSecrets"]["GatewayConnect"]["SaSKeys"]["Secondary"]

      # Debug Only
      self.logger.debug("[SCOPE ID]: %s" % self.scope_id)
      self.logger.debug("[DEVICE PRIMARY KEY]: %s" % self.device_primary_key)
      self.logger.debug("[DEVICE SECONDARY KEY]: %s" % self.device_secondary_key)
      self.logger.debug("[GATEWAY PRIMARY KEY]: %s" % self.gateway_primary_key)
      self.logger.debug("[GATEWAY SECONDARY KEY]: %s" % self.gateway_secondary_key)
      return
    
    def get_provisioning_host(self):
      return self.provisioning_host

    def get_scope_id(self):
      return self.scope_id

    def get_device_primary_key(self):
      return self.device_primary_key

    def get_device_secondary_key(self):
      return self.device_secondary_key      

    def get_gateway_primary_key(self):
      return self.gateway_primary_key      

    def get_gateway_secondary_key(self):
      return self.gateway_secondary_key     