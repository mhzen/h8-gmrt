import cv2
from ultralytics import YOLO
import requests, time
import serial
import json

# Settings constant
model = YOLO('./model/v4.pt')
mode = 'image' # 'image', 'video', 'webcam', 'webcam_image'
path = './test2.jpg' # kalo pake video atau image
width = 1920
height = 1080
conf = 0.8 # 0.7-0.8 to be safe
url = "http://127.0.0.1:8000/update_coords"  # ganti sesuai kebutuhan
connection = 'usb' # usb or wifi or none
serialAddress = '/dev/pts/5' # ganti sesuai kebutuhan, default /dev/ttyUSB0 for linux

# Initialize
print(model.names)
cap = None # Capture (frame yg kontinyu)
single_frame = None # Single frame
ser = None

# Validate mode and initialize source
if mode == 'webcam':
    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

elif mode == 'webcam_image':
    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    success, single_frame = cap.read()
    cap.release()
    if not success or single_frame is None:
        print("Failed to capture webcam image")
        exit(1)

elif mode in ('image', 'video'):
    if mode == 'image':
        single_frame = cv2.imread(path)
        if single_frame is None:
            print(f"Failed to read image at {path}")
            exit(1)
    else:  # mode == 'video'
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"Failed to open video at {path}")
            exit(1)

else:
    print(f"Unknown mode: {mode}")
    exit(1)

# TODO: setup geometry (miringnya kamera), kalibrasi, dst

def setup_serial():
    global ser # Gunakan variabel global
    if connection == 'usb':
        try:
            # Buka port SATU KALI
            ser = serial.Serial(serialAddress, 9600, timeout=1)
            print(f"Koneksi USB dibuka di {serialAddress}")
        except Exception as e:
            print(f"Gagal membuka port serial {serialAddress}: {e}")
            exit(1) # Keluar jika port gagal dibuka

# Send coordinates via HTTP POST or serial
# TODO: masukkin ke fungsi
def send(x, y, width_box, height_box):
    data = {"x": x, "y": y, "width": width_box, "height": height_box, "timestamp": time.time()}
    headers = {'Content-Type': 'application/json'}
    if connection == 'usb':
        if ser:
            try:
                json_string = json.dumps(data)
                ser.write(f"{json_string}\n".encode())
                print("Coordinates sent via USB")
            except Exception as e:
                print(f"Error sending coordinates via USB: {e}")
        else:
            print("Serial connection not established.")
    elif connection == 'wifi':
        try:
            response = requests.post(url, json=data, headers=headers, timeout=5)
            if response.status_code == 200:
                print("Coordinates sent successfully")
            else:
                print(f"Failed to send coordinates, status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending coordinates: {e}")

# x (relatif ke resolusi x webcam)
# y (relatif ke resolusi y webcam)
# width (panjang total frame)
# height (lebar total frame)
# time (waktu deteksi, butuh ga ya?)

setup_serial()

if single_frame is not None:
    results = model.track(single_frame, conf=conf)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            cv2.circle(single_frame, (cx, cy), 5, (255, 0, 0), -1)
            print(f"x: {cx}, y: {cy}")
            cv2.putText(single_frame, f"{cx},{cy}", (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

            # send coordinates for this detection
            if connection is not None:
                send(cx, cy, width, height)

    if len(results) > 0:
        cv2.imshow("Image", results[0].plot())
    else:
        cv2.imshow("Image", single_frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    while cap is not None:
        success, frame = cap.read()
        if not success:
            break

        results = model.track(frame, conf=conf)

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                print(f"x: {cx}, y: {cy}")
                cv2.putText(frame, f"{cx},{cy}", (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

                # send coordinates for this detection
                if connection is not None:
                    send(cx, cy, width, height)

        if len(results) > 0:
            cv2.imshow("Live Camera", results[0].plot())
        else:
            cv2.imshow("Live Camera", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()