from kinematics import RobotArmModel
from comms import RobotNetwork
from gui import RobotGUI

def run_studio():
    # 1. สร้างระบบสมองกล
    robot_model = RobotArmModel()
    
    # 2. สร้างระบบเชื่อมต่อ
    robot_network = RobotNetwork(ip="192.168.1.106", port=4210)
    
    # 3. นำทั้งหมดมาประกอบเข้ากับหน้าจอ
    app = RobotGUI(model=robot_model, network=robot_network)
    
    # 4. เริ่มรันโปรแกรม
    print("Starting Robot Studio GUI...")
    app.mainloop()

if __name__ == "__main__":
    run_studio()