from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

# Load model YOLO (pakai versi ringan)
model = YOLO('/Users/mhah/Documents/EVERYTHING CODE RELATED/gmrt/object-detection-using-webcam/yolo11s.pt')

# Deteksi objek pada gambar
results = model('gambar.jpg')

# Tampilkan hasil deteksi
results[0].show()  # otomatis buka jendela dengan bounding 