import asyncio
import struct

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

PUMP_NAME = "Ard Pump Lo"
PUMP_CHAR = "00002a67-0000-1000-8000-00805f9b34fb"
HUMIDITY_CHAR = "00002a68-0000-1000-8000-00805f9b34fb"


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

    print("Connecting to pump 0")

    async with BleakClient(pumps[0].address) as client:
        print("Connected to pump0, getting services")

        services = await client.get_services()
        for service in services:
            print(service)
            for char in service.characteristics:
                print(f"-> {char}")

        pump_state = await client.read_gatt_char(PUMP_CHAR)
        print(f"pump state: {pump_state}")

        humidity_state = await client.read_gatt_char(HUMIDITY_CHAR)
        print(f"humidity state: {humidity_state}, {struct.unpack('f', humidity_state)}")


asyncio.run(main())
