import cv2
from ultralytics import YOLO
import socket, struct

model = YOLO('./object-detection-using-webcam/model.pt')
print(model.names)
webcamera = cv2.VideoCapture(0)
# webcamera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# webcamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# UDP sender to mock ESP32 server
SERVER_ADDR = ("127.0.0.1", 5005)
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

            # pack and send coordinates: header = [start(1), cmd(1), length(2)], payload = int32 x, int32 y
            # start byte 0xAA, command 0x02, payload length 8 bytes
            packet = struct.pack('!BBHii', 0xAA, 0x02, 8, cx, cy)
            udp_sock.sendto(packet, SERVER_ADDR)

    if len(results) > 0:
        cv2.imshow("Live Camera", results[0].plot())

    if cv2.waitKey(1) == ord('q'):
        break

udp_sock.close()
webcamera.release()
cv2.destroyAllWindows()