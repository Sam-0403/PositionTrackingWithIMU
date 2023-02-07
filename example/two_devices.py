import asyncio

from bleak import BleakClient

temperatureUUID = "45366e80-cf3a-11e1-9ab4-0002a5d5c51b"
ecgUUID = "46366e80-cf3a-11e1-9ab4-0002a5d5c51b"

notify_uuid = 13
# notify_uuid = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(0xFFE1)


def callback(characteristic, data):
    print(characteristic, data)


async def connect_to_device(address, loop):
    print("starting", address, "loop")
    async with BleakClient(address, loop=loop, timeout=10.0) as client:

        print("connect to", address)
        try:
            await client.start_notify(notify_uuid, callback)
            await asyncio.sleep(10.0, loop=loop)
            await client.stop_notify(notify_uuid)
        except Exception as e:
            print(e)

    print("disconnect from", address)


def main(addresses):
    loop = asyncio.get_event_loop()

    tasks = asyncio.gather(
        *(connect_to_device(address, loop) for address in addresses)
    )

    loop.run_until_complete(tasks)


if __name__ == "__main__":
    asyncio.run(
        main(
            [
                "0CE4468C-F05D-CE69-B2D9-F03D72FB9130",
                "2204480E-DFE9-9C03-827A-B92E59BFE617",
            ]
        )
    )