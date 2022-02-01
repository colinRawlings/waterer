import asyncio
import struct
from contextlib import AsyncExitStack
from time import time

import matplotlib.pyplot as plt
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

plt.ion()

from waterer_backend.status_log import BinaryStatusLog, FloatStatusLog

PUMP_NAME = "Ard Pump Lo"
PUMP_ATTR_ID = "00002a67-0000-1000-8000-00805f9b34fb"
PUMP_STATUS_ATTR_ID = "00002a68-0000-1000-8000-00805f9b34fb"
HUMIDITY_ATTR_ID = "00002a69-0000-1000-8000-00805f9b34fb"


async def main():
    print("Scanning for devices for 10s ... ")
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

    pumps = [device for device in devices if device.name == PUMP_NAME]

    print(f"Found: {len(pumps)} pump(s):")

    for pump in pumps:
        print(pump)

    if len(pumps) == 0:
        print("No pumps exiting")
        return

    async with AsyncExitStack() as stack:
        clients = [await stack.enter_async_context(BleakClient(pump)) for pump in pumps]

        #     for mgr in [BleakClient(pump) for pump in pumps]:
        #         stack.enter_context(mgr)

        # for index, pump in enumerate(pumps):
        #     print(f"Connecting to pump {index}")

        #     async with BleakClient(pumps[index].address) as client:

        for index, client in enumerate(clients):
            print(f"Connected to pump {index}, getting services")
            services = await client.get_services()
            for service in services:
                print(service)
                for char in service.characteristics:
                    print(f"-> {char}")

            pump_state = await client.read_gatt_char(PUMP_ATTR_ID)
            print(f"pump state: {pump_state}")

            # def float_from_bytes(bytes_arr: bytes)->float:
            #     return 1000*struct.unpack('f', bytes_arr)[0] # type: ignore

            # def bool_from_bytes(bytes_arr: bytes)->bool:
            #     return struct.unpack('b', bytes_arr)[0] # type: ignore

            # async def get_humidity_mV()->float:
            #     humidity_bytes = await client.read_gatt_char(HUMIDITY_ATTR_ID)
            #     return float_from_bytes(humidity_bytes)

            # async def get_pump_status()->bool:
            #     status_bytes = await client.read_gatt_char(PUMP_STATUS_ATTR_ID)
            #     return bool_from_bytes(status_bytes)

            # humidity_mV = await get_humidity_mV()
            # pump_status = await get_pump_status()

            # print(f"humidity mV: {humidity_mV:.1f} mV")
            # print(f"status: {pump_status}")

            # pump_status_log = BinaryStatusLog()
            # humidity_log = FloatStatusLog()
            # T0 = time()

            # while True:
            #     pump_status_sample = await get_pump_status()
            #     pump_status_log.add_sample(time()-T0, pump_status_sample)

            #     humdity_sample = await get_humidity_mV()
            #     humidity_log.add_sample(time()- T0, humdity_sample)

            #     t,H = humidity_log.get_values()
            #     plt.plot(t, H, ".-b")

            #     await asyncio.sleep(5)
            #     plt.pause(1)


asyncio.run(main())
