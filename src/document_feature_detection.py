import cv2
from deepface import DeepFace
import numpy as np
from pytesseract import image_to_string
from typing import List, Dict, Any
from ultralytics import YOLO

model = YOLO("get-verified.pt")
model.eval()

labels = ["braille", "flag", "id_design", "identity_card",
          "identity_number", "image", "names", "signature", "surname"]


def bytes_to_image(bytes: bytes) -> np.ndarray:
    nd_array: np.ndarray = np.frombuffer(bytes, np.uint8)

    return cv2.imdecode(nd_array, cv2.IMREAD_COLOR)


def model_predict(image) -> List[Dict[str, Any]]:
    results = model.predict(image, verbose=False)

    boxes: List[Dict[str, Any]] = []

    for result in results:
        for box in result.boxes:
            cls: int = int(box.cls[0])
            label = labels[cls - 1]
            confidence: float = box.conf[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            text: str | None = None

            if label == "identity_number" or label == "names" or label == "surname":
                text = image_to_string(
                    image[y1:y2, x1:x2], lang="eng").strip()

            boxes.append({
                "center": [(x1 + x2) / 2, (y1 + y2) / 2],
                "confidence": confidence,
                "coordinates": [x1, y1, x2, y2],
                "label": label,
                "text": text if text else None
            })

    return boxes


def document_feature_detection(bytes: bytes):
    image: np.ndarray = cv2.cvtColor(bytes_to_image(bytes), cv2.COLOR_BGR2RGB)

    boxes: List[Dict[str, Any]] = model_predict(image)

    return boxes


def verify_identity_document(bytes: bytes, boxes: List[Dict[str, Any]], face: bytes | None = None):
    braille_box = next((x for x in boxes if x["label"] == "braille"), None)

    flag_box = next((x for x in boxes if x["label"] == "flag"), None)

    id_design_box = next((x for x in boxes if x["label"] == "id_design"), None)

    identity_card_box = next(
        (x for x in boxes if x["label"] == "identity_card"), None)

    identity_number_box = next(
        (x for x in boxes if x["label"] == "identity_number"), None)

    image_box = next((x for x in boxes if x["label"] == "image"), None)

    names_box = next(
        (x for x in boxes if x["label"] == "names" and x['text']), None)

    signature_box = next((x for x in boxes if x["label"] == "signature"), None)

    surname_box = next(
        (x for x in boxes if x["label"] == "surname" and x['text']), None)

    if braille_box is None or flag_box is None or id_design_box is None or identity_card_box is None or identity_number_box is None or image_box is None or names_box is None or signature_box is None or surname_box is None:
        return False

    image: np.ndarray = bytes_to_image(bytes)

    x1, y1, x2, y2 = image_box['coordinates']

    if face is not None:
        result = DeepFace.verify(
            img1_path=image[y1:y2, x1:x2],
            img2_path=bytes_to_image(face),
        )

        return result['verified']

    return True
