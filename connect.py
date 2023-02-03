import asyncio
from bleak import BleakClient
import binascii
import threading
import time

address = "0CE4468C-F05D-CE69-B2D9-F03D72FB9130"
# MODEL_NBR_UUID = "0x5CAF2260-3CEB-379A-AC70-12F8660AB7F1"
counter = 0
G = 9.8

def notification_handler(sender, data):
    global counter
    """Simple notification handler which prints the data received."""
    # print("{0}: {1}".format(sender, len(data)))
    print("{0}: {1}".format(counter, binascii.hexlify(data)))

    acc_x, acc_y, acc_z = int.from_bytes(data[2:4], "little", signed="True")/32768*16*G, int.from_bytes(data[4:6], "little", signed="True")/32768*16*G, int.from_bytes(data[6:8], "little", signed="True")/32768*16*G
    w_x, w_y, w_z = int.from_bytes(data[8:10], "little", signed="True")/32768*2000, int.from_bytes(data[10:12], "little", signed="True")/32768*2000, int.from_bytes(data[12:14], "little", signed="True")/32768*2000
    roll, pitch, yaw = int.from_bytes(data[14:16], "little", signed="True")/32768*180, int.from_bytes(data[16:18], "little", signed="True")/32768*180, int.from_bytes(data[18:20], "little", signed="True")/32768*180
    # acc_x, acc_y, acc_z = (data[3]*256+data[2])/32768*16*G, (data[5]*256+data[4])/32768*16*G, (data[7]*256+data[6])/32768*16*G
    # w_x, w_y, w_z = (data[9]*256+data[8])/32768*2000, (data[11]*256+data[10])/32768*2000, (data[13]*256+data[12])/32768*2000
    # roll, pitch, yaw = (data[15]*256+data[14])/32768*180, (data[17]*256+data[16])/32768*180, (data[19]*256+data[18])/32768*180

    print(f"{counter}: [acc: {acc_x}, {acc_y}, {acc_z}, w: {w_x}, {w_y}, {w_z}]")
    print(f"{counter}: [roll: {roll}, pitch: {pitch}, yaw: {yaw}]")
    counter += 1

def input_handler(client: BleakClient):
    while True:
        msgWrite = input()
        if msgWrite == "mag":
            print("Mag!!")
        if msgWrite == "exit": 
            client.stop_notify(13)
            break

async def main(address):
    async with BleakClient(address) as client:
        # model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        # print("Model Number: {0}".format("".join(map(chr, model_number))))

        await client.start_notify(13, notification_handler)

        readThread = threading.Thread(target=input_handler, args=[client])
        readThread.setDaemon(True)
        readThread.start()
        # await input_handler(client)

        # await asyncio.sleep(20.0)
        # await client.stop_notify(13)

asyncio.run(main(address))