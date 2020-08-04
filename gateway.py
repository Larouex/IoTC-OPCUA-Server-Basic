
# ==================================================================================
#   File:   gateway.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Transparent Gateway OPC Server for Telemetry to Azure IoT Central
#
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import  hmac, getopt, sys, time, binascii, \
        struct, string, threading, asyncio, os

import logging as Log
    
# our classes
from Classes.config import Config
from Classes.gateway import Gateway

# Workers
config_data = None

# -------------------------------------------------------------------------------
#   Start Gateway
# -------------------------------------------------------------------------------
async def start_gateway(WhatIf):

  gateway = Gateway(Log, WhatIf)
  await gateway.start()
  return True

async def main(argv):

    # execution state from args
    whatif = False

    short_options = "hvdw"
    long_options = ["help", "verbose", "debug", "whatif"]
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print (str(err))
    
    for current_argument, current_value in arguments:

      if current_argument in ("-h", "--help"):
          print("HELP for gateway.py")
          print("------------------------------------------------------------------------------------------------------------------")
          print("-h or --help - Print out this Help Information")
          print("-v or --verbose - Debug Mode with lots of Data will be Output to Assist with Debugging")
          print("-d or --debug - Debug Mode with lots of DEBUG Data will be Output to Assist with Tracing and Debugging")
          print("-w or --whatif - Combine with Verbose it will Output the Configuration sans starting the Server")
          print("------------------------------------------------------------------------------------------------------------------")
          return

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

    await start_gateway(whatif)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

