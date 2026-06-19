from utils.yolo_detector import detect_vehicles
import numpy as np

dummy = np.zeros((640, 640, 3), dtype=np.uint8)

result = detect_vehicles(dummy)

print(type(result))
print(len(result))