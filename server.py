# ==================================================================================
#   File:   server.py
#   Author: Larry W Jordan Jr (larouex@gmail.com)
#   Use:    Simple OPC/UA Server for testing Azure IoT Central Scenarios
#
#   Online:   www.hackinmakin.com
#
#   (c) 2020 Larouex Software Design LLC
#   This code is licensed under MIT license (see LICENSE.txt for details)    
# ==================================================================================
import  getopt, sys, time, string, threading, asyncio, os
import logging as Log

# opcua
from asyncua import ua, Server
from asyncua.common.methods import uamethod

# our classes
from Classes.opcserver import OpcServer
from Classes.config import Config
from Classes.varianttype import VariantType


# -------------------------------------------------------------------------------
#   Start the OPC Server
# -------------------------------------------------------------------------------
async def start_server(WhatIf):

  # Start Server
  opc_server = OpcServer(Log, WhatIf)
  await opc_server.start()

  return

# -------------------------------------------------------------------------------
#   OPC Server Loop for Telemetry
# -------------------------------------------------------------------------------
async def loop_server(OpcServer):

  # Loop and Send Node->Variable Telemetry
  opc_server = OpcServer

  async with opc_server:
    while True:
        await asyncio.sleep(1)
        await opc_server.loop()


async def main(argv):

    whatif = False

    # execution state from args
    short_options = "hvw"
    long_options = ["help", "verbose", "whatif"]
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print (str(err))
    
    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--help"):
            print("HELP for server.py")
            print("------------------------------------------------------------------------------------------------------------------")
            print("-h or --help - Print out this Help Information")
            print("-v or --verbose - Debug Mode with lots of Data will be Output to Assist with Debugging")
            print("-w or --whatif - Combine with Verbose it will Output the Configuration sans starting the Server")
            print("------------------------------------------------------------------------------------------------------------------")
            sys.exit()
        
        if current_argument in ("-v", "--verbose"):
            Log.basicConfig(format="%(levelname)s: %(message)s", level=Log.DEBUG)
            Log.info("Verbose mode...")
        else:
            Log.basicConfig(format="%(levelname)s: %(message)s")

        if current_argument in ("-w", "--whatif"):
            whatif = True
            Log.info("Whatif Mode...")

    # Start Server
    await start_server(whatif)
    #await loop_server(opc_server)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

