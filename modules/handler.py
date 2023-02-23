# import aioconsole
# from ..config import *

class Handler:
    def __init__(self, index, client, instruction, write_handler):
        self.index = index
        self.client = client

        self.instruction = instruction
        self.write_handler = write_handler

        self.acc_buffer = [0]*3
        self.ang_vel_buffer = [0]*3
        self.ang_buffer = [0]*3
        self.quat_buffer = [0]*4

    def get_current_buffer(self):
        return {
            "Index": self.index,
            "Acc": self.acc_buffer,
            "Gyro": self.ang_vel_buffer,
            "Ang": self.ang_buffer,
            "Quat": self.quat_buffer,
        }

    def notification_notify_handler(self, sender, data):
        """
        Data converter for notify message ([Acc, Angular_velocity, Angle])
        """
        # global sender_buffer, acc_buffer, ang_vel_buffer, ang_buffer
        acc = [0]*3
        for i, j in zip(range(2, 8, 2), range(3)):
            # acc[j] = round(-int.from_bytes(data[i:i+2], "little", signed="True")/32768*16*9.8, 5)
            acc[j] = round(-int.from_bytes(data[i:i+2], "little", signed="True")/32768*16, 5)
        ang_vel = [0]*3
        for i, j in zip(range(8, 14, 2), range(3)):
            ang_vel[j] = round(-int.from_bytes(data[i:i+2], "little", signed="True")/32768*2000, 5)
        ang = [0]*3
        for i, j in zip(range(14, 20, 2), range(3)):
            ang[j] = round(int.from_bytes(data[i:i+2], "little", signed="True")/32768, 5)
        
        # acc_glb = rotate(ang[0]*np.pi, ang[1]*np.pi, ang[2]*np.pi, acc)
        # acc_buffer[sender_buffer[sender]] = list(acc_glb)

        self.acc_buffer = list(acc)
        self.ang_vel_buffer = list(ang_vel)
        self.ang_buffer = list(ang)

    def notification_write_handler(self, sender, data):
        """
        Data converter for quaternion message
        """
        # global sender_buffer, quat_buffer
        quat = [0]*4
        for i, j in zip(range(4, 12, 2), range(4)):
            quat[j] = round(int.from_bytes(data[i:i+2], "little", signed="True")/32768*16, 5)

        self.quat_buffer = list(quat)
        # print(self.index)

    async def notification_handler(self, sender, data):
        """
        The notification handler which decode the received data and stored in the corresponding buffers
        """
        # global sender_buffer, acc_buffer, ang_vel_buffer, ang_buffer, quat_buffer
        # print("{0}: {1}".format(sender, len(data)))
        # print("{0}: {1}".format(counter, binascii.hexlify(data)))

        # if sender not in self.sender_buffer:
        #     # print(sender)
        #     self.sender_buffer[sender] = len(self.acc_buffer)
        #     # acc_buffer.append([0]*3)
            # ang_vel_buffer.append([0]*3)
            # ang_buffer.append([0]*3)
            # quat_buffer.append([0]*4)

        while len(data)>=20:
            if data[0:2]==b'\x55\x61':
                self.notification_notify_handler(sender, data)
                # await client.write_gatt_char(write_handler, instruction["Q"])
                
            if data[0:2]==b'\x55\x71':
                if data[2]==0x51:
                    self.notification_write_handler(sender, data)
                    # global write_handler, instruction
                    # try:
                    await self.client.write_gatt_char(self.write_handler, self.instruction["Q"])
                    # except:
                    #     await aioconsole.aprint("Write Error")
        
            data = data[20:]

        # await aioconsole.aprint(f"[{sender_buffer[sender]}] data in")

        # await aioconsole.aprint(sender)
        # await aioconsole.aprint(f"[acc: {acc_x}, {acc_y}, {acc_z}, w: {w_x}, {w_y}, {w_z}]")
        # await aioconsole.aprint(f"{counter}: [roll: {roll}, pitch: {pitch}, yaw: {yaw}]")