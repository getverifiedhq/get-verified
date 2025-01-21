import cv2
from io import BytesIO
import misc
import numpy as np
import pytesseract
from ultralytics import YOLO

model = YOLO("get-verified.pt")


def execute(filename: str):
    with open(filename, "rb") as f:
        bytes = f.read()

    nd_array = np.frombuffer(bytes, np.uint8)

    image = cv2.cvtColor(cv2.imdecode(
        nd_array, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    results = model(image)

    boxes = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = box.conf[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center_x, center_y = [(x1 + x2) / 2, (y1 + y2) / 2]
            text = None

            if class_id == 4 or class_id == 6 or class_id == 8:
                text = pytesseract.image_to_string(
                    image[y1:y2, x1:x2], lang="eng").strip()

            boxes.append({
                "center": [center_x, center_y],
                "class_id": class_id,
                "confidence": confidence,
                "coordinates": [x1, y1, x2, y2],
                "text": text if text else None
            })

    return boxes


filename = "test-0.png"

boxes = execute(filename)

flag_center = next((x["center"] for x in boxes if x["class_id"] == 1), None)

id_design_center = next((x["center"]
                        for x in boxes if x["class_id"] == 2), None)

angle = misc.calculate_angle(
    flag_center[0], flag_center[1], id_design_center[0], id_design_center[1])

# 2 - rotate right 90
# -174 - rotate left 90
# 94 - nothing
# -86 - rotate 180

identity_number = next((x["text"] for x in boxes if x["class_id"] == 4), None)

parsed_identity_number = misc.parse_identity_number(identity_number)

obj = {
    "surname": next((x["text"] for x in boxes if x["class_id"] == 8), None),
    "names": next((x["text"] for x in boxes if x["class_id"] == 6), None),
    "sex": parsed_identity_number["gender"],
    "nationality": "RSA",
    "identity_number": identity_number,
    "date_of_birth": parsed_identity_number["date_of_birth"],
    "country_of_birth": "RSA",
    "status": "CITIZEN"
}

print(obj)
