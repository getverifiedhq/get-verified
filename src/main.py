import cv2
from document_feature_detection import bytes_to_image, document_feature_detection, verify_identity_document
import sys

filename = sys.argv[1]

with open(filename, "rb") as f:
    bytes = f.read()
    
face = None

if len(sys.argv) == 3:
    with open(sys.argv[2], "rb") as f:
        face = f.read()

boxes = document_feature_detection(bytes)

print(boxes)

obj = verify_identity_document(bytes, boxes, face) if boxes is not None else None

print(obj)

image = bytes_to_image(bytes)

for box in boxes:
    x1, y1, x2, y2 = map(int, box["coordinates"])

    cv2.rectangle(image, (x1, y1), (x2, y2),
                    color=(255, 91, 99), thickness=1)

cv2.imwrite("output.png", image)