# ==================================================================================
#   File:   scandevices.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Raspberry Pi "Protocol Translation" Gateway for Azure IoT Central
#           This module scans for devices and updates the devicescache. We run
#           it seperate as it is SUDO and we do not want to install our packages
#           tec under sudo
#
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import  getopt, sys, time, string, threading, asyncio, os
import logging as Log

# our classes
from classes.scanfordevices import ScanForDevices
from classes.config import Config

# -------------------------------------------------------------------------------
#   Scan For Devices
# -------------------------------------------------------------------------------
async def scan_for_devices(BluetoothInterface, ResetHCI, ScanSeconds):
  if not 'SUDO_UID' in os.environ.keys():
    print("[ERROR][STOPPED] Scanning Devices requires Super User Priveleges")
    sys.exit(1)

  scanfordevices = ScanForDevices(Log, BluetoothInterface, ResetHCI, ScanSeconds)
  await scanfordevices.scan_for_devices()
  return True

async def main(argv):

    # execution state from args
    is_resethci = False
    scan_seconds = 0
    bluetooth_interface = -1

    short_options = "hvrb:s:"
    long_options = ["help", "verbose", "resethci", "btiface=", "scanseconds="]
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print (str(err))
    
    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--help"):
            print("HELP for scandevices.py")
            print("------------------------------------------------------------------------------------------------------------------")
            print("-h or --help - Print out this Help Information")
            print("-v or --verbose - Debug Mode with lots of Data will be Output to Assist with Debugging")
            print("-b or --btiface - Bluetooth Interface? '0' = Built in or '1' if you added a BT Device and Antenna, etc. (default=0)")
            print("-r or --resethci - OS command to Reset the Bluetooth Interface (default=false)")
            print("-s or --scanseconds - Number of Seconds the BLE Scan should Scan for Devices (default=10)")
            print("------------------------------------------------------------------------------------------------------------------")
            sys.exit()

        if current_argument in ("-v", "--verbose"):
            Log.basicConfig(format="%(levelname)s: %(message)s", level=Log.DEBUG)
            Log.info("Verbose mode...")
        else:
            Log.basicConfig(format="%(levelname)s: %(message)s")
        
        if current_argument in ("-r", "--resethci"):
            Log.info("Bluetooth Reset Interface mode...")
            is_resethci = True
        
        if current_argument in ("-b", "--btiface"):
            Log.info("Bluetooth Interface Override...%s" % current_value)
            btiface = current_value

        if current_argument in ("-s", "--scanseconds"):
            Log.info("Scan Seconds Override...%s" % current_value)
            scan_seconds = current_value
    
    # Load Configuration File
    config = Config(Log)
    config_data = config.data
    
    if scan_seconds == 0:
      scan_seconds = config_data["ScanSeconds"]

    if bluetooth_interface == -1:
      bluetooth_interface = config_data["BluetoothInterface"]

    await scan_for_devices(BluetoothInterface=bluetooth_interface, ResetHCI=is_resethci, ScanSeconds=scan_seconds)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

