import cv2
from ultralytics import YOLO
import socket, struct, time, json

model = YOLO('./object-detection-using-webcam/model.pt')
print(model.names)
webcamera = cv2.VideoCapture(0)

# TCP client to mock ESP32 server
SERVER_ADDR = ("127.0.0.1", 5005)
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.settimeout(5)
try:
    tcp_sock.connect(SERVER_ADDR)
    print("Connected to mock ESP32 TCP server", SERVER_ADDR)
except Exception as e:
    print("Failed to connect to server:", e)
    tcp_sock = None

def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf

# todo: setup geometry (miringnya kamera)

while True:
    success, frame = webcamera.read()
    if not success:
        break

    results = model.track(frame, classes=67, conf=0.8)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
            print(f"x: {cx}, y: {cy}")
            cv2.putText(frame, f"{cx},{cy}", (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

            if tcp_sock:
                try:
                    # pack and send coordinates: header = [start(1), cmd(1), length(2)], payload = int32 x, int32 y
                    packet = struct.pack('!BBHii', 0xAA, 0x02, 8, cx, cy)
                    tcp_sock.sendall(packet)
                    # receive response header and payload
                    hdr = recv_exact(tcp_sock, 4)
                    if hdr:
                        _, cmd, plen = struct.unpack('!BBH', hdr)
                        payload = recv_exact(tcp_sock, plen) if plen > 0 else b''
                        if payload:
                            try:
                                resp = json.loads(payload.decode('utf-8'))
                                print("Server response:", resp)
                            except Exception:
                                print("Non-JSON payload:", payload)
                except Exception as e:
                    print("TCP send/recv error:", e)
                    try:
                        tcp_sock.close()
                    except:
                        pass
                    tcp_sock = None

    if len(results) > 0:
        cv2.imshow("Live Camera", results[0].plot())

    if cv2.waitKey(1) == ord('q'):
        break

if tcp_sock:
    tcp_sock.close()
webcamera.release()
cv2.destroyAllWindows()