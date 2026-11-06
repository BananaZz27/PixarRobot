import socket

class RobotNetwork:
    def __init__(self, ip="192.168.1.106", port=4210):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Network Initialized -> Target: {self.ip}:{self.port}")

        # ตั้งค่า Limit ต่ำสุด-สูงสุด ของมอเตอร์แต่ละข้อต่อ (อ้างอิงตามค่า 0-1023 ของ SCS15)
        # ลำดับคือ [ฐาน(J1), ไหล่(J2), ศอก(J3), คอ(J4), หัว(J5)]
        self.limits = [
            (0, 1023),    # J1 ฐาน (สมมติว่าหมุนได้สุด)
            (87, 1022),   # J2 ไหล่ (ID 9) ล็อกตามที่คุณวัดมา
            (27, 949),    # J3 ศอก (เดี๋ยวมาแก้เพิ่มทีหลังได้)
            (235, 841),    # J4 คอ
            (0, 1023)     # J5 หัว
        ]

    def send_joints(self, joints):
        """ แปลงองศา (-150 ถึง 150) เป็นสเกล SCS15 และล็อกไม่ให้เกิน Limit """
        try:
            mapped_joints = []
            for i, angle in enumerate(joints):
                # 1. แปลงองศาเป็นสเกล 0-1023
                servo_val = int(((angle + 150.0) / 300.0) * 1023.0)
                
                # 2. ดึงค่า Limit ของข้อต่อนี้มาใช้
                min_limit, max_limit = self.limits[i]
                
                # 3. บังคับล็อกค่าไม่ให้ทะลุ Limit เด็ดขาด
                servo_val = max(min_limit, min(max_limit, servo_val))
                mapped_joints.append(servo_val)

            payload = f"{mapped_joints[0]},{mapped_joints[1]},{mapped_joints[2]},{mapped_joints[3]},{mapped_joints[4]}"
            
            print(f"Sending UDP: {payload}")
            self.sock.sendto(payload.encode('utf-8'), (self.ip, self.port))
            
        except Exception as e:
            print(f"UDP Error: {e}")