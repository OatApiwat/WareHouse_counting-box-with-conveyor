import socket
import threading
import signal
import sys

SERVER_IP = "169.254.52.155"
SERVER_PORT = 5001
clients = {}  # {ip: socket}
server = None  # ตัวแปรเก็บ server socket

def handle_client(client_socket, client_address):
    ip = client_address[0]
    print(f"[NEW CONNECTION] {ip} connected.")
    clients[ip] = client_socket

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            decoded_data = data.decode('utf-8').strip()
            print(f"[RECEIVED] From {ip}: {decoded_data}")

            # ส่งไปให้ Client2
            if "169.254.52.155" in clients and ip != "169.254.52.155":
                clients["169.254.52.155"].sendall(data)

            # ส่งไปให้ Client3 ถ้าเป็นข้อมูลจาก Client2
            if "169.254.52.177" in clients and ip == "169.254.52.155":
                clients["169.254.52.177"].sendall(data)

    except:
        print(f"[DISCONNECTED] {ip} disconnected.")
    finally:
        clients.pop(ip, None)
        client_socket.close()

def stop_server(signal, frame):
    """ ฟังก์ชันหยุดเซิร์ฟเวอร์เมื่อกด Ctrl+C """
    print("\n[SHUTTING DOWN] Closing server and all connections...")
    for client in clients.values():
        client.close()
    if server:
        server.close()
    sys.exit(0)

def start_server():
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)
    print(f"[LISTENING] Server listening on {SERVER_IP}:{SERVER_PORT}")

    # ดักจับสัญญาณ Ctrl+C เพื่อปิด server
    signal.signal(signal.SIGINT, stop_server)

    while True:
        try:
            client_socket, client_address = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
        except:
            break

if __name__ == "__main__":
    start_server()