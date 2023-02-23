import asyncio
from bleak import BleakClient
import binascii
import threading
import csv

address = "0CE4468C-F05D-CE69-B2D9-F03D72FB9130"
# MODEL_NBR_UUID = "0x5CAF2260-3CEB-379A-AC70-12F8660AB7F1"
counter = 0
sample_rate = 200

is_running = True

mag = [0]*3
buffer = []

instruction = {
    "M": b'\xff\xaa\x27\x3a\x00', 
    "Q": b'\xff\xaa\x27\x51\x00', 
    "H": b'\xff\xaa\x27\x40\x00',
    "P": b'\xff\xaa\x27\x64\x00',
    "R": b'\xff\xaa\x00\x01\x00',
}

def save_data():
    global buffer, counter
    print(counter)

    file = open('LoggedData_CalInertialAndMag.csv', 'w', newline='')
    writer = csv.writer(file)

    title_str = "Packet number,Gyroscope X (deg/s),Gyroscope Y (deg/s),Gyroscope Z (deg/s),Accelerometer X (g),Accelerometer Y (g),Accelerometer Z (g),Magnetometer X (G),Magnetometer Y (G),Magnetometer Z (G)"
    title = title_str.split(",")
    writer.writerow(title)
    for sample in buffer:
        writer.writerow(sample)


def notification_handler(sender, data):
    global counter, buffer, mag
    """Simple notification handler which prints the data received."""
    # print("{0}: {1}".format(sender, len(data)))
    # print("{0}: {1}".format(counter, binascii.hexlify(data)))

    while len(data)>=20:
        if data[0:2]==b'\x55\x61':
            acc = [0]*3
            for i, j in zip(range(2, 8, 2), range(3)):
                acc[j] = -int.from_bytes(data[i:i+2], "little", signed="True")/32768*16 

            gyro = [0]*3
            for i, j in zip(range(8, 14, 2), range(3)):
                gyro[j] = int.from_bytes(data[i:i+2], "little", signed="True")/32768*2000/180  

            if not mag==[0, 0, 0]:     
                buffer.append([
                    counter, 
                    gyro[0], gyro[1], gyro[2], 
                    acc[0], -acc[1], -acc[2], 
                    mag[0], mag[1], mag[2]
                ])
                counter += 1

        if data[0:4]==b'\x55\x71\x3a\x00':
            for i, j in zip(range(4, 10, 2), range(3)):
                mag[j] = int.from_bytes(data[i:i+2], "little", signed="False")/100

        data = data[20:]

    
    # acc_x, acc_y, acc_z = int.from_bytes(data[2:4], "little", signed="True")/32768*16*G, int.from_bytes(data[4:6], "little", signed="True")/32768*16*G, int.from_bytes(data[6:8], "little", signed="True")/32768*16*G
    # w_x, w_y, w_z = int.from_bytes(data[8:10], "little", signed="True")/32768*2000, int.from_bytes(data[10:12], "little", signed="True")/32768*2000, int.from_bytes(data[12:14], "little", signed="True")/32768*2000
    # roll, pitch, yaw = int.from_bytes(data[14:16], "little", signed="True")/32768*180, int.from_bytes(data[16:18], "little", signed="True")/32768*180, int.from_bytes(data[18:20], "little", signed="True")/32768*180
    # acc_x, acc_y, acc_z = (data[3]*256+data[2])/32768*16*G, (data[5]*256+data[4])/32768*16*G, (data[7]*256+data[6])/32768*16*G
    # w_x, w_y, w_z = (data[9]*256+data[8])/32768*2000, (data[11]*256+data[10])/32768*2000, (data[13]*256+data[12])/32768*2000
    # roll, pitch, yaw = (data[15]*256+data[14])/32768*180, (data[17]*256+data[16])/32768*180, (data[19]*256+data[18])/32768*180

    # print(f"{counter}: [acc: {acc_x}, {acc_y}, {acc_z}, w: {w_x}, {w_y}, {w_z}]")
    # print(f"{counter}: [roll: {roll}, pitch: {pitch}, yaw: {yaw}]")
    # counter += 1

def input_handler():
    global is_running
    while True:
        msgWrite = input()
        if msgWrite == "mag":
            print("Mag!!")
        if msgWrite == "q": 
            is_running = False
            break

async def main(address):
    async with BleakClient(address) as client:
        # model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        # print("Model Number: {0}".format("".join(map(chr, model_number))))

        print("Connected")

        readThread = threading.Thread(target=input_handler)
        readThread.setDaemon(True)
        readThread.start()
        # await input_handler(client)

        await client.write_gatt_char(16, instruction["M"])
        await client.start_notify(13, notification_handler)

        global is_running, sample_rate
        t = 1.0/sample_rate
        while is_running:
            await client.write_gatt_char(16, instruction["M"])
            await asyncio.sleep(t)
        # await asyncio.sleep(20.0)
        await client.stop_notify(13)

asyncio.run(main(address))
save_data()