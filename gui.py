import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RobotGUI(ctk.CTk):
    def __init__(self, model, network):
        super().__init__()
        
        self.model = model
        self.network = network
        self.last_send_time = 0
        self.timer_id = None

        self.title("PIXAR LAMP - 5 DOF ROBOT STUDIO (SCS15)")
        self.geometry("1100x700")

        self.setup_ui()
        self.update_visualizer()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # แผงควบคุม (ซ้าย)
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, width=350, corner_radius=10)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_propagate(False)

        ctk.CTkLabel(self.left_frame, text="State & Kinematics", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(15, 10))

        self.value_labels = []
        self.sliders = [] # เก็บลิสต์ของ Slider ไว้เผื่อสั่งรีเซ็ต
        joint_names = ["J1: Base (Pan)", "J2: Shoulder (Pitch)", "J3: Elbow (Pitch)", "J4: Neck (Pitch)", "J5: Head (Roll)"]
        
        for i in range(5):
            frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
            frame.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(frame, text=joint_names[i], width=120, anchor="w").pack(side="left")
            
            val_lbl = ctk.CTkLabel(frame, text=f"{self.model.joints[i]}°", width=40)
            val_lbl.pack(side="right")
            self.value_labels.append(val_lbl)
            
            slider = ctk.CTkSlider(frame, from_=-150, to=150, command=lambda v, idx=i: self.on_slider_move(v, idx))
            slider.set(self.model.joints[i])
            slider.pack(side="right", expand=True, padx=10)
            self.sliders.append(slider) # บันทึก Slider เก็บไว้

        # ป้ายแสดงพิกัด
        ctk.CTkLabel(self.left_frame, text="Actual Tool Center Point (TCP)", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.tcp_label = ctk.CTkLabel(self.left_frame, text="X: 0.00 mm\nY: 0.00 mm\nZ: 0.00 mm", font=ctk.CTkFont(size=16), text_color="#00FFCC")
        self.tcp_label.pack(pady=5)

        # ------------------------------------------
        # เพิ่มปุ่ม Reset Position ตรงนี้
        # ------------------------------------------
        self.reset_btn = ctk.CTkButton(self.left_frame, text="RESET POSITION", fg_color="#C0392B", hover_color="#922B21", font=ctk.CTkFont(weight="bold"), command=self.reset_robot)
        self.reset_btn.pack(pady=(30, 10), fill="x", padx=40)

        # ==========================================
        # แผง 3D (ขวา)
        # ==========================================
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

        plt.style.use('dark_background')
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.fig.patch.set_facecolor('#2B2B2B')
        
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#2B2B2B')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def on_slider_move(self, value, idx):
        angle = int(value)
        
        # 1. อัปเดตตัวเลขและกราฟิก 3D ทันทีให้ผู้ใช้เห็นภาพ
        self.model.set_joint(idx, angle)
        self.value_labels[idx].configure(text=f"{angle}°")
        self.update_visualizer()
        
        # 2. ยกเลิกคิวส่งข้อมูลเดิมหากผู้ใช้ยังลากเมาส์ไม่เสร็จ
        if hasattr(self, 'timer_id') and self.timer_id is not None:
            self.after_cancel(self.timer_id)
            
        # 3. ตั้งเวลาส่งข้อมูลใหม่: ถ้าหยุดลากสไลเดอร์เกิน 0.2 วินาที (200ms) ถึงจะส่งคำสั่งไปที่บอร์ด
        self.timer_id = self.after(200, self.send_to_robot)

    def send_to_robot(self):
        """ ฟังก์ชันสำหรับส่งข้อมูลแบบครั้งเดียวจบ """
        self.network.send_joints(self.model.joints)

    def reset_robot(self):
        """ ฟังก์ชันสำหรับรีเซ็ตหุ่นยนต์กลับไปท่าเริ่มต้น """
        # ท่ามาตรฐาน (Home Position)
        home_joints = [0, 90, -90, 0, 0]
        
        for i in range(5):
            # อัปเดตค่ากลับไปที่สมอง
            self.model.set_joint(i, home_joints[i])
            # บังคับ Slider ให้เลื่อนกลับ
            self.sliders[i].set(home_joints[i])
            # อัปเดตตัวหนังสือ
            self.value_labels[i].configure(text=f"{home_joints[i]}°")
            
        # อัปเดตกราฟิก 3D และส่งคำสั่งไปให้ NodeMCU
        self.update_visualizer()
        self.network.send_joints(self.model.joints)
        print("Robot position reset to HOME.")

    def update_visualizer(self):
        self.ax.clear()

        # ดึงพิกัดจากไฟล์ kinematics
        pts = self.model.get_forward_kinematics()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]

        # วาดเส้นและแกน
        self.ax.plot(xs, ys, zs, color="#00FFCC", linewidth=4, marker='o', markersize=8, markerfacecolor="white")
        self.ax.quiver(xs[-1], ys[-1], zs[-1], 30, 0, 0, color='r', linewidth=2) 
        self.ax.quiver(xs[-1], ys[-1], zs[-1], 0, 30, 0, color='g', linewidth=2) 
        self.ax.quiver(xs[-1], ys[-1], zs[-1], 0, 0, 30, color='b', linewidth=2) 

        # วาดฐาน
        theta = np.linspace(0, 2*np.pi, 100)
        self.ax.plot(100*np.cos(theta), 100*np.sin(theta), 0, color="gray", linestyle='dashed')

        limit = 250
        self.ax.set_xlim([-limit, limit])
        self.ax.set_ylim([-limit, limit])
        self.ax.set_zlim([0, limit])

        # อัปเดตตัวหนังสือ
        tcp = self.model.get_tcp()
        self.tcp_label.configure(text=f"X: {tcp[0]:.2f} mm\nY: {tcp[1]:.2f} mm\nZ: {tcp[2]:.2f} mm")

        self.canvas.draw()