import cv2
from deepface import DeepFace
import numpy as np
from pytesseract import image_to_string
from typing import List, Dict, Any
from ultralytics import YOLO

model = YOLO("get-verified.pt")
model.eval()


def bytes_to_image(bytes: bytes) -> np.ndarray:
    nd_array: np.ndarray = np.frombuffer(bytes, np.uint8)

    return cv2.imdecode(nd_array, cv2.IMREAD_COLOR)


def model_predict(image) -> List[Dict[str, Any]]:
    results = model.predict(image, verbose=False)

    boxes: List[Dict[str, Any]] = []

    for result in results:
        for box in result.boxes:
            class_id: int = int(box.cls[0])
            confidence: float = box.conf[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            text: str | None = None

            if class_id == 4 or class_id == 6 or class_id == 8:
                text = image_to_string(
                    image[y1:y2, x1:x2], lang="eng").strip()

                # if class_id == 4:
                #     text = re.findall(r'\d+', text)[0] if text else None

            boxes.append({
                "center": [(x1 + x2) / 2, (y1 + y2) / 2],
                "class_id": class_id,
                "confidence": confidence,
                "coordinates": [x1, y1, x2, y2],
                "text": text if text else None
            })

    return boxes


def document_feature_detection(bytes: bytes):
    image: np.ndarray = cv2.cvtColor(bytes_to_image(bytes), cv2.COLOR_BGR2RGB)

    boxes: List[Dict[str, Any]] = model_predict(image)

    return boxes


def verify_identity_document(bytes: bytes, boxes: List[Dict[str, Any]]):
    braille_box = next((x for x in boxes if x["class_id"] == 0), None)

    flag_box = next((x for x in boxes if x["class_id"] == 1), None)

    id_design_box = next((x for x in boxes if x["class_id"] == 2), None)

    identity_card_box = next((x for x in boxes if x["class_id"] == 3), None)

    identity_number_box = next(
        (x for x in boxes if x["class_id"] == 4 and x['text']), None)

    image_box = next((x for x in boxes if x["class_id"] == 5), None)

    names_box = next(
        (x for x in boxes if x["class_id"] == 6 and x['text']), None)

    signature_box = next((x for x in boxes if x["class_id"] == 7), None)

    surname_box = next(
        (x for x in boxes if x["class_id"] == 8 and x['text']), None)

    if braille_box is None or flag_box is None or id_design_box is None or identity_card_box is None or identity_number_box is None or image_box is None or names_box is None or signature_box is None or surname_box is None:
        return False

    image: np.ndarray = bytes_to_image(bytes)

    x1, y1, x2, y2 = image_box['coordinates']

    result = DeepFace.verify(
        img1_path=image[y1:y2, x1:x2],
        img2_path="Screenshot 2025-01-28 at 13.27.39.png",
    )

    print(result)

    return True
