import aioboto3
import asyncio
import boto3
from concurrent.futures import ThreadPoolExecutor
import cv2
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from get_verified import analyze, predict_thread
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

executor = ThreadPoolExecutor()


async def upload(bytes: bytes, key: str):
    session = aioboto3.Session()

    async with session.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    ) as client:
        await client.put_object(
            Bucket=os.getenv("AWS_S3_BUCKET"),
            Key=key,
            Body=bytes,
            ContentType="image/png",
            ACL="public-read"
        )

    return f'https://{os.getenv("AWS_S3_BUCKET")}.s3.amazonaws.com/{key}'


async def upload_image(image):
    _, nd_array = await asyncio.get_event_loop().run_in_executor(executor, cv2.imencode, '.png', image)

    return await upload(nd_array.tobytes(), f"result/{uuid.uuid4()}")


@app.post("/api/v1")
async def upload_post(request: Request):
    try:
        body = await request.body()

        boxes = predict_thread(body, None)

        if boxes is None:
            return {"success": False}

        ###
        nd_array = np.frombuffer(body, np.uint8)

        image = cv2.imdecode(
            nd_array, cv2.IMREAD_COLOR)

        for box in boxes:
            x1, y1, x2, y2 = map(int, box["coordinates"])

            try:
                if box["class_id"] == 4 or box["class_id"] == 6:
                    image[y1:y2, x1:x2] = cv2.GaussianBlur(
                        image[y1:y2, x1:x2], (21, 21), 0)
                
                if box["class_id"] == 5:
                    image[y1:y2, x1:x2] = cv2.GaussianBlur(
                        image[y1:y2, x1:x2], (101, 101), 0)
            except:
                print('ERROR')

            cv2.rectangle(image, (x1, y1), (x2, y2),
                          color=(255, 91, 99), thickness=1)

        [_, url] = await asyncio.gather(
            upload(body, f"raw/{uuid.uuid4()}"),
            upload_image(image)
        )
        ###

        data = analyze(boxes)

        if data is None:
            return {"boxes": boxes, "success": False, "url": url}

        return {"boxes": boxes, "data": data, "success": True, "url": url}
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT")))

# curl -X POST "http://127.0.0.1:8080/api/v1" -H "Content-Type: application/octet-stream" --data-binary "@test.png"
