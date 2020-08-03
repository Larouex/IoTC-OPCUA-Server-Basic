# ==================================================================================
#   File:   provisiondevices.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Simple OPC/UA Server for testing Azure IoT Central Scenarios.
#           This module provisions devices and updates the devicescache. 
#           It either re-provisions all devices or just those that have null in
#           LastProvisioned option in the file i.e "LastProvisioned": null
#
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import  getopt, sys, time, string, threading, asyncio, os
import logging as Log

# our classes
from Classes.provisiondevices import ProvisionDevices
from Classes.config import Config

# -------------------------------------------------------------------------------
#   Provision Devices
# -------------------------------------------------------------------------------
async def provision_devices(ProvisioningScope, GatewayType):

  provisiondevices = ProvisionDevices(Log, ProvisioningScope, GatewayType)
  await provisiondevices.provision_devices()
  return True

async def main(argv):

    # execution state from args
    provisioning_scope = None
    gateway_type = None

    short_options = "hvp:g:"
    long_options = ["help", "verbose", "provisioningscope=", "gatewaytype="]
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print (str(err))
    
    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--help"):
            print("HELP for provisiondevices.py")
            print("------------------------------------------------------------------------------------------------------------------")
            print("-h or --help - Print out this Help Information")
            print("-v or --verbose - Debug Mode with lots of Data will be Output to Assist with Debugging")
            print("-d or --debug - Debug Mode with lots of DEBUG Data will be Output to Assist with Tracing and Debugging")
            print("-w or --whatif - Combine with Verbose it will Output the Configuration sans starting the Server")
            print("------------------------------------------------------------------------------------------------------------------")
            sys.exit()
        
        if current_argument in ("-v", "--verbose"):
            Log.basicConfig(format="%(levelname)s: %(message)s", level=Log.DEBUG)
            Log.info("Verbose mode...")
        else:
            Log.basicConfig(format="%(levelname)s: %(message)s")
        
        if current_argument in ("-p", "--provisioningscope"):
            Log.info("Provisioning Scope Override...%s" % current_value)
            provisioning_scope = current_value

        if current_argument in ("-g", "--gatewaytype"):
            Log.info("Gateway Type  Override...%s" % current_value)
            gateway_type = current_value

    # Load Configuration File
    config = Config(Log)
    config_data = config.data
    
    if provisioning_scope == None:
      provisioning_scope = config_data["ProvisioningScope"]

    if gateway_type == None:
      gateway_type = config_data["GatewayType"]

    await provision_devices(ProvisioningScope=provisioning_scope, GatewayType=gateway_type)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

