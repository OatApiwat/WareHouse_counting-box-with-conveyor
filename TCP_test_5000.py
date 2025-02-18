import socket
import time

def send_tcp_messages(server_ip, server_port, client_ip, start, end):
    try:
        # สร้างการเชื่อมต่อ TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # กำหนด IP ของ client
            client_socket.bind((client_ip, 0))  # Port 0 จะเลือก port ที่ว่างให้โดยอัตโนมัติ
            client_socket.connect((server_ip, server_port))

            # ส่งข้อความตั้งแต่ start ถึง end
            for i in range(start, end + 1):
                message = ("11;;;ZMBSD0020_002_01        TMSC64626     {i}       {end}      SELANGOR,MALAYSIA     60        "
                           "17PS-M058-G3W    009-0029048     7475002589**11;;;17PS-M058-G3W     T25205-01     40").format(i=i, end=end)
                client_socket.sendall(message.encode('utf-8'))
                print(f"Sent: {message}")
                time.sleep(0.5)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # กำหนดข้อมูลเซิร์ฟเวอร์
    SERVER_IP = "169.254.52.155"
    SERVER_PORT = 5001
    
    # กำหนด IP ของ client
    CLIENT_IP = "169.254.52.160"
    
    # ส่งค่าจาก 1 ถึง 10
    send_tcp_messages(SERVER_IP, SERVER_PORT, CLIENT_IP, 1, 10)
