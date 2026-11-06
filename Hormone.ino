#include <WiFi.h>
#include <WiFiUdp.h>
#include <SCServo.h> 

const char* ssid = "Clinostat"; 
const char* password = "12345678";

WiFiUDP udp;
const int udpPort = 4210;
char packetBuffer[64];

SCSCL sc; 

#define RXD2 16
#define TXD2 17

void setup() {
  Serial.begin(115200); 
  
  Serial1.begin(1000000, SERIAL_8N1, RXD2, TXD2);
  sc.pSerial = &Serial1;

  Serial.print("Connecting Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  Serial.println("\nIP: " + WiFi.localIP().toString());

  udp.begin(udpPort);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    String data = "";
    
    // --- ส่วนสำคัญ: วนลูปอ่านคิวที่ค้างอยู่ทั้งหมด เอาเฉพาะข้อมูล "ชุดล่าสุด" ---
    while (packetSize) {
      int len = udp.read(packetBuffer, 64);
      if (len > 0) {
        packetBuffer[len] = 0;
        data = String(packetBuffer);
      }
      packetSize = udp.parsePacket(); // เช็คว่ามีคิวเหลืออีกไหม
    }
    
    data.trim();
    // Serial.println("Latest: " + data); // เปิดไว้เช็คได้ถ้าต้องการ
    
    int servo_ids[5] = {4, 9, 7, 2, 1}; 
    int startIndex = 0;
    
    for (int i = 0; i < 5; i++) {
      int commaIndex = data.indexOf(',', startIndex);
      String valStr;
      
      if (commaIndex != -1) {
        valStr = data.substring(startIndex, commaIndex);
        startIndex = commaIndex + 1;
      } else {
        valStr = data.substring(startIndex); 
      }
      
      int targetPosition = valStr.toInt();
      int current_id = servo_ids[i];
      
      // --- ปรับให้หมุนสมูทขึ้น (ใช้ Speed = 2000 แทนการหมุนแบบกระชาก) ---
      sc.WritePos(current_id, targetPosition, 1000, 0); 
    }
  }
}