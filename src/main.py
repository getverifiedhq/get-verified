import cv2
import misc
import numpy as np
import pytesseract
import re
from ultralytics import YOLO

model = YOLO("get-verified.pt")


def execute(bytes: bytes, rotate_code: int | None):
    nd_array = np.frombuffer(bytes, np.uint8)

    image = cv2.cvtColor(cv2.imdecode(
        nd_array, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    if rotate_code is not None:
        image = cv2.rotate(image, rotate_code)

    results = model.predict(image, verbose=False)

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

                if class_id == 4:
                    text = re.findall(r'\d+', text)[0] if text else None

            boxes.append({
                "center": [center_x, center_y],
                "class_id": class_id,
                "confidence": confidence,
                "coordinates": [x1, y1, x2, y2],
                "text": text if text else None
            })

    flag_center = next((x["center"]
                       for x in boxes if x["class_id"] == 1), None)

    if (flag_center is None):
        return None

    id_design_center = next((x["center"]
                            for x in boxes if x["class_id"] == 2), None)

    if (id_design_center is None):
        return None

    angle = misc.calculate_angle(
        flag_center[0], flag_center[1], id_design_center[0], id_design_center[1])

    # 2 - rotate right 90
    # -174 - rotate left 90
    # 94 - nothing
    # -86 - rotate 180

    if (angle > -45 and angle <= 45):
        return execute(bytes, cv2.ROTATE_90_CLOCKWISE)

    if (angle > -225 and angle <= -135):
        return execute(bytes, cv2.ROTATE_90_COUNTERCLOCKWISE)

    if (angle > -135 and angle <= -45):
        return execute(bytes, cv2.ROTATE_180)

    return boxes


filename = "test.png"

with open(filename, "rb") as f:
    bytes = f.read()

boxes = execute(bytes, None)

braille = next((x for x in boxes if x["class_id"] == 0), None)

flag = next((x for x in boxes if x["class_id"] == 1), None)

id_design = next((x for x in boxes if x["class_id"] == 2), None)

identity_card = next((x for x in boxes if x["class_id"] == 3), None)

identity_number = next(
    (x for x in boxes if x["class_id"] == 4 and x['text']), None)

image = next((x for x in boxes if x["class_id"] == 5), None)

names = next((x for x in boxes if x["class_id"] == 6 and x['text']), None)

signature = next((x for x in boxes if x["class_id"] == 7), None)

surname = next((x for x in boxes if x["class_id"] == 8 and x['text']), None)

if braille is None or flag is None or id_design is None or identity_card is None or identity_number is None or image is None or names is None or signature is None or surname is None:
    raise RuntimeError

parsed_identity_number = misc.parse_identity_number(identity_number["text"])

obj = {
    "surname": surname['text'] if surname else None,
    "names": names['text'] if names else None,
    "sex": parsed_identity_number["gender"],
    "nationality": "RSA",
    "identity_number": identity_number["text"],
    "date_of_birth": parsed_identity_number["date_of_birth"],
    "country_of_birth": "RSA",
    "status": "CITIZEN" if parsed_identity_number["citizen"] else None
}

print(obj)
