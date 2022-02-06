import asyncio
import logging

from bleak import BleakClient, BleakScanner
from waterer_backend.BLE.BLEpump_manager import PumpManagerContext
from waterer_backend.config import get_pumps_config


async def main():
    logging.basicConfig(level=logging.INFO)

    pumps_config = get_pumps_config()

    async with PumpManagerContext(settings=pumps_config[0]) as manager:
        manager.start()
        # await manager.turn_on(1, 1)
        await manager.turn_on(0, 1000)
        await asyncio.sleep(20)


asyncio.run(main())
