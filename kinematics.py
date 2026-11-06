import math

class RobotArmModel:
    def __init__(self):
        # ความยาวของแต่ละข้อต่อแขนกล (มิลลิเมตร)
        self.L1 = 50.0  # ฐานถึงไหล่
        self.L2 = 120.0 # ไหล่ถึงศอก
        self.L3 = 120.0 # ศอกถึงคอ
        self.L4 = 40.0  # คอถึงปลายโคมไฟ
        
        # มุมเริ่มต้นของ Servo ทั้ง 5 ตัว (องศา)
        self.joints = [0, 90, -90, 0, 0]

    def set_joint(self, idx, angle):
        """ อัปเดตค่ามุมของข้อต่อ """
        self.joints[idx] = angle

    def get_forward_kinematics(self):
        """ คำนวณพิกัด 3D ของข้อต่อทุกชิ้น """
        rads = [math.radians(a) for a in self.joints]
        
        x0, y0, z0 = 0, 0, 0
        x1, y1, z1 = 0, 0, self.L1
        
        # J2 (Shoulder Pitch)
        x2 = x1 + self.L2 * math.cos(rads[1]) * math.cos(rads[0])
        y2 = y1 + self.L2 * math.cos(rads[1]) * math.sin(rads[0])
        z2 = z1 + self.L2 * math.sin(rads[1])
        
        # J3 (Elbow Pitch)
        angle_j3 = rads[1] + rads[2]
        x3 = x2 + self.L3 * math.cos(angle_j3) * math.cos(rads[0])
        y3 = y2 + self.L3 * math.cos(angle_j3) * math.sin(rads[0])
        z3 = z2 + self.L3 * math.sin(angle_j3)
        
        # J4 (Neck Pitch - TCP)
        angle_j4 = angle_j3 + rads[3]
        x4 = x3 + self.L4 * math.cos(angle_j4) * math.cos(rads[0])
        y4 = y3 + self.L4 * math.cos(angle_j4) * math.sin(rads[0])
        z4 = z3 + self.L4 * math.sin(angle_j4)

        return [(x0,y0,z0), (x1,y1,z1), (x2,y2,z2), (x3,y3,z3), (x4,y4,z4)]

    def get_tcp(self):
        """ คืนค่าพิกัดจุดปลายสุด """
        points = self.get_forward_kinematics()
        return points[-1]