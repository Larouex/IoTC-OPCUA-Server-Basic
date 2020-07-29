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
from Classes.config import Config
from Classes.varianttype import VariantType


# -------------------------------------------------------------------------------
#   Provision Devices
# -------------------------------------------------------------------------------
async def provision_devices(ProvisioningScope, GatewayType):

  provisiondevices = ProvisionDevices(Log, ProvisioningScope, GatewayType)
  await provisiondevices.provision_devices()
  return True

async def main(argv):

    # Nodes
    nodes = []
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

    # Load Configuration File
    config = Config(Log)
    config_data = config.data

    # Data Type Mappings
    variant_type = VariantType(Log)
    
    # OPCUA Server Setup
    if not whatif:
        opc_server = Server()
        await opc_server.init()
        opc_url = config_data["UrlPattern"].format(id = 199, port = 4840)
        Log.info("[URL] OPC Server IP %s" % opc_url)
        opc_server.set_endpoint(opc_url)

    # Our NameSpace
    namespace = config_data["NameSpace"]
    Log.info("[NAMESPACE] ID %s" % namespace)
    if not whatif:
        id_namespace = await opc_server.register_namespace(namespace)

    # Create our Nodes and Parameters
    for node in config_data["Nodes"]:
        name = node["Name"]
        Log.info("[NODE NAME] %s" % name)
        
        # Add Node  and Begin Populating our Address Space
        #node_obj = await server.nodes.objects.add_object(id_namespace, name)
        
        for variable in node["Variables"]:
            variable_name = variable["DisplayName"]
            Log.info("[VARIABLE DISPLAY NAME] %s" % variable_name)
            range_value = variable["RangeValues"][0]
            Log.info("[RANGE VALUE] %s" % range_value)
            opc_variant_type = variant_type.map_variant_type(variable["IoTCDataType"])
            Log.info("[IoTC DATA TYPE] %s" % variable["IoTCDataType"])
            Log.info("[VARIANT DATA TYPE] %s" % opc_variant_type)
            Log.info("[DATA TYPE] %s" % opc_variant_type)

            if not whatif:
                variable_obj = await node_obj.add_variable(id_namespace, variable_name, range_value, varianttype=opc_variant_type, datatype=opc_variant_type)
                await variable_obj.set_writable()
                #await server.nodes.objects.add_method(ua.NodeId('ServerMethod', 2), ua.QualifiedName('ServerMethod', 2), func, [ua.VariantType.Int64], [ua.VariantType.Int64])
                Log.info("[STARTING SERVER] %s" % opc_url)
    

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

