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
async def provision_devices(Whatif, Id):

  provisiondevices = ProvisionDevices(Log, Whatif, Id)
  await provisiondevices.provision_devices()
  return True

async def main(argv):

    # execution state from args
    whatif = False
    id = None

    short_options = "hvdwi:"
    long_options = ["help", "verbose", "debug", "whatif", "iddevice="]
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
            print("-i or --iddevice - This ID will get appended to your Device. Example '001' = larouex-industrial-manufacturing-001")
            print("------------------------------------------------------------------------------------------------------------------")
            sys.exit()
        
        if current_argument in ("-v", "--verbose"):
            Log.basicConfig(format="%(levelname)s: %(message)s", level=Log.INFO)
            Log.info("Verbose Logging Mode...")
        else:
            Log.basicConfig(format="%(levelname)s: %(message)s")

        if current_argument in ("-d", "--debug"):
            Log.basicConfig(format="%(levelname)s: %(message)s", level=Log.DEBUG)
            Log.info("Debug Logging Mode...")
        else:
            Log.basicConfig(format="%(levelname)s: %(message)s")

        if current_argument in ("-w", "--whatif"):
            whatif = True
            Log.info("Whatif Mode...")

        if current_argument in ("-i", "--iddevice"):
            id = current_value
            Log.info("File Name is Specified...")

    await provision_devices(whatif, id)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

