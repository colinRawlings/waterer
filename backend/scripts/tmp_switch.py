import asyncio
import struct
from contextlib import AsyncExitStack
from time import time

import waterer_backend.BLE.BLE_ids as ids

# import matplotlib.pyplot as plt
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from waterer_backend.status_log import BinaryStatusLog, FloatStatusLog

# plt.ion()


PUMP_NAME = "Ard Pump Lo"
PUMP_ATTR_ID = "00002a67-0000-1000-8000-00805f9b34fb"
PUMP_STATUS_ATTR_ID = "00002a68-0000-1000-8000-00805f9b34fb"
HUMIDITY_ATTR_ID = "00002a69-0000-1000-8000-00805f9b34fb"


ACTIVATION_TIME_MS = 2000


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

        for index, client in enumerate(clients):
            print(f"Connected to pump {index}, getting services")
            services = await client.get_services()
            for service in services:
                print(service)
                for char in service.characteristics:
                    print(f"-> {char}")

            attrs = {
                "pump": ids.PUMP_ATTR_ID,
                "pump_status": ids.PUMP_STATUS_ATTR_ID,
                "humidity": ids.HUMIDITY_ATTR_ID,
            }

            for attr_name in attrs:
                state = await client.read_gatt_char(attrs[attr_name])
                print(f"{attr_name}: {state}")

            client = clients[1]

            await client.write_gatt_char(
                attrs["pump"], struct.pack("<I", ACTIVATION_TIME_MS)
            )


asyncio.run(main())
