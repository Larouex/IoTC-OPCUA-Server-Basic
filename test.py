import asyncio
import logging as Log

from asyncua import Client, ua, Node

from Classes.config import Config
from Classes.maptelemetry import MapTelemetry

# logging.basicConfig(level=logging.INFO)

class SubHandler(object):
    def datachange_notification(self, node, val, data):
        # print("New data change event", node, val, data)
        print("New data change event", node, val)

    def event_notification(self, event):
        print("New event", event)


async def run():
    url = "opc.tcp://localhost:4840/Larouex-Industrial-Manufacturing/Server"

    map_telemetry_file = MapTelemetry(Log)
    map_telemetry_file.load_file()
    map_telemetry_data = map_telemetry_file.data

    config_file = Config(Log)
    config_file_data = config_file.data

    async with Client(url=url) as client:
        idx =  await client.get_namespace_index(map_telemetry_data["NameSpace"])
        print(idx)

        while True:
          await asyncio.sleep(config_file_data["ClientFrequencyInSeconds"])

          for node in map_telemetry_data["Nodes"]:
            print(node["Name"])
            for variable in node["Variables"]:
              print(variable["DisplayName"])
              print(variable["TelemetryName"])
              read_node = client.get_node(variable["NodeId"])
              val = await read_node.get_value()
              print(val)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())