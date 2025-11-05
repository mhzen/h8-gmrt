import cv2
from ultralytics import YOLO

model = YOLO('/Users/mhah/Documents/EVERYTHING CODE RELATED/gmrt/object-detection-using-webcam/yolo11s.pt')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    results = model.track(frame)



    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            print(f"Detected object at (x={cx}, y={cy})")
        

    cv2.imshow("Frame", results[0].plot())
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()