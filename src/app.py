import boto3
import cv2
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from get_verified import analyze, predict
import numpy as np
import os
import uuid
import uvicorn

load_dotenv()

app = FastAPI()

boto3Client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)


def upload_image(image):
    _, nd_array = cv2.imencode('.png', image)

    key = f"get-verified/other/{uuid.uuid4()}"

    boto3Client.put_object(
        Bucket=os.getenv("AWS_S3_BUCKET"),
        Key=key,
        Body=nd_array.tobytes(),
        ContentType="image/png",
        ACL="public-read"
    )

    return f'https://{os.getenv("AWS_S3_BUCKET")}.s3.amazonaws.com/{key}'


@app.post("/api/v1")
async def upload_post(request: Request):
    try:
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

        if boxes is None:
            return {"success": False}

        data = analyze(boxes)

        if data is None:
            return {"success": False}

        ###
        nd_array = np.frombuffer(body, np.uint8)

        image = cv2.cvtColor(cv2.imdecode(
            nd_array, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

        for box in boxes:
            x1, y1, x2, y2 = map(int, box["coordinates"])

            cv2.rectangle(image, (x1, y1), (x2, y2),
                          color=(255, 91, 99), thickness=2)

        data["url"] = upload_image(image)
        ###

        return {"boxes": boxes, "data": data, "success": True, "url": url}
    except:
        return {"success": False}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT")))

# curl -X POST "http://127.0.0.1:8080/api/v1" -H "Content-Type: application/octet-stream" --data-binary "@test.png"
