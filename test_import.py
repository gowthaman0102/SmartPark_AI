from utils.yolo_detector import detect_vehicles
import numpy as np

img = np.zeros((640, 640, 3), dtype=np.uint8)

result = detect_vehicles(img)

print(type(result))
print(len(result))
print(result)