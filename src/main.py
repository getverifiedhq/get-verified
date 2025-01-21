from ultralytics import YOLO
import cv2
import pytesseract
import misc

model = YOLO("get-verified.pt")


def execute(filename: str):
    results = model(filename)

    image = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)

    boxes = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = box.conf[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            text = None

            if class_id == 4 or class_id == 6 or class_id == 8:
                text = pytesseract.image_to_string(
                    image[y1:y2, x1:x2], lang="eng").strip()

            boxes.append({
                "class_id": class_id,
                "confidence": confidence,
                "coordinates": [x1, y1, x2, y2],
                "text": text if text else None
            })

    return boxes


filename = "test.png"

boxes = execute(filename)

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
