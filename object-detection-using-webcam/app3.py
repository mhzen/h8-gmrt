import cv2
from ultralytics import YOLO  # install via: pip install ultralytics opencv-python

class GenericObjectDetector:
    def __init__(self, model_path="yolov8n.pt", conf_thresh=0.5):
        self.model = YOLO(model_path)
        self.conf_thresh = conf_thresh

    def detect(self, image):
        H, W = image.shape[:2]
        results = self.model(image)
        detections = []
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf < self.conf_thresh:
                    continue
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                w = x2 - x1
                h = y2 - y1
                detections.append({
                    "rel_x": x1 / W,
                    "rel_y": y1 / H,
                    "rel_w": w / W,
                    "rel_h": h / H,
                    "confidence": conf
                })
        return detections

def run_webcam(detector, camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to get frame from webcam.")
            break

        detections = detector.detect(frame)
        # you can draw boxes if you like:
        for det in detections:
            x = int(det["rel_x"] * frame.shape[1])
            y = int(det["rel_y"] * frame.shape[0])
            w = int(det["rel_w"] * frame.shape[1])
            h = int(det["rel_h"] * frame.shape[0])
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)
            cv2.putText(frame, f"{det['confidence']:.2f}", (x, y-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        cv2.imshow("Webcam Generic Object Detection", frame)

        # press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = GenericObjectDetector(model_path="yolov8n.pt", conf_thresh=0.4)
    run_webcam(detector, camera_index=0)
