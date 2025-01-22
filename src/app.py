import boto3
import cv2
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import misc
import numpy as np
import os
import pytesseract
import re
from ultralytics import YOLO
import uuid
import uvicorn

load_dotenv()

app = FastAPI()

model = YOLO("get-verified.pt")

boto3Client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)


def predict(bytes: bytes, rotate_code: int | None):
    nd_array = np.frombuffer(bytes, np.uint8)

    image = cv2.cvtColor(cv2.imdecode(
        nd_array, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    if rotate_code is not None:
        image = cv2.rotate(image, rotate_code)

    height, width = image.shape[:2]

    results = model.predict(image, verbose=False)

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

                # if class_id == 4:
                #     text = re.findall(r'\d+', text)[0] if text else None

            boxes.append({
                "center": [(x1 + x2) / 2, (y1 + y2) / 2],
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

    if (angle > -45 and angle <= 45):
        return predict(bytes, cv2.ROTATE_90_CLOCKWISE)

    if (angle > -225 and angle <= -135):
        return predict(bytes, cv2.ROTATE_90_COUNTERCLOCKWISE)

    if (angle > -135 and angle <= -45):
        return predict(bytes, cv2.ROTATE_180)

    for box in boxes:
        coordinates = box["coordinates"] if rotate_code is None else misc.rotate_coordinates(box["coordinates"][0], box["coordinates"][1], box["coordinates"][2], box["coordinates"][3], width, height, {
            cv2.ROTATE_90_CLOCKWISE: cv2.ROTATE_90_COUNTERCLOCKWISE,
            cv2.ROTATE_90_COUNTERCLOCKWISE: cv2.ROTATE_90_CLOCKWISE,
            cv2.ROTATE_180: cv2.ROTATE_180,
        }[rotate_code])

        center = [(coordinates[0] + coordinates[2]) / 2,
                  (coordinates[1] + coordinates[3]) / 2]

        box["coordinates"] = coordinates
        box["center"] = center

    return boxes


def analyze(boxes):
    braille = next((x for x in boxes if x["class_id"] == 0), None)

    flag = next((x for x in boxes if x["class_id"] == 1), None)

    id_design = next((x for x in boxes if x["class_id"] == 2), None)

    identity_card = next((x for x in boxes if x["class_id"] == 3), None)

    identity_number = next(
        (x for x in boxes if x["class_id"] == 4 and x['text']), None)

    image = next((x for x in boxes if x["class_id"] == 5), None)

    names = next((x for x in boxes if x["class_id"] == 6 and x['text']), None)

    signature = next((x for x in boxes if x["class_id"] == 7), None)

    surname = next(
        (x for x in boxes if x["class_id"] == 8 and x['text']), None)

    if braille is None or flag is None or id_design is None or identity_card is None or identity_number is None or image is None or names is None or signature is None or surname is None:
        return None

    parsed_identity_number = misc.parse_identity_number(
        identity_number["text"])

    return {
        "surname": surname['text'] if surname else None,
        "names": names['text'] if names else None,
        "sex": parsed_identity_number["gender"],
        "nationality": "RSA",
        "identity_number": identity_number["text"],
        "date_of_birth": parsed_identity_number["date_of_birth"],
        "country_of_birth": "RSA",
        "status": "CITIZEN" if parsed_identity_number["citizen"] else None
    }


@app.post("/api/upload")
async def upload_post(request: Request):
    body = await request.body()

    key = f"get-verified/{uuid.uuid4()}"

    boto3Client.put_object(
        Bucket=os.getenv("AWS_S3_BUCKET"),
        Key=key,
        Body=body,
        ContentType="image/png",
        ACL="public-read"
    )

    url = f'https://{os.getenv("AWS_S3_BUCKET")}.s3.amazonaws.com/{key}'

    boxes = predict(body, None)

    result = analyze(boxes)

    ###
    # nd_array = np.frombuffer(body, np.uint8)

    # image = cv2.cvtColor(cv2.imdecode(
    #     nd_array, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    # for box in boxes:
    #     x1, y1, x2, y2 = map(int, box["coordinates"])

    #     cv2.rectangle(image, (x1, y1), (x2, y2),
    #                   color=(0, 255, 0), thickness=2)

    # cv2.imwrite("out.png", image)
    ###

    return {"boxes": boxes, "result": result, "url": url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT")))

# curl -X POST "http://127.0.0.1:8080/api/upload" -H "Content-Type: application/octet-stream" --data-binary "@test.png"
