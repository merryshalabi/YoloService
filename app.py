import os
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from PIL import Image
from ultralytics import YOLO
import boto3
import torch

from storage.sqlite_storage import SQLiteStorage
from storage.dynamodb_storage import DynamoDBStorage

# Disable GPU usage
torch.cuda.is_available = lambda: False

# Initialize FastAPI
app = FastAPI()

# Set up directories
UPLOAD_DIR = "uploads/original"
PREDICTED_DIR = "uploads/predicted"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PREDICTED_DIR, exist_ok=True)

# Load YOLO model
model = YOLO("yolov8n.pt")

# Set up S3
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
s3_client = boto3.client("s3")

# Select storage backend
storage_type = os.getenv("STORAGE_TYPE", "sqlite")
if storage_type == "dynamodb":
    storage = DynamoDBStorage()
else:
    storage = SQLiteStorage()


@app.post("/predict")
async def predict(request: Request):
    uid = str(uuid.uuid4())

    try:
        body = await request.json()
        image_name = body.get("image_name")
        if not image_name:
            raise HTTPException(status_code=400, detail="Missing image_name in JSON body")

        ext = os.path.splitext(image_name)[1]
        if ext not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(status_code=400, detail="Invalid image file extension")

        original_path = os.path.join(UPLOAD_DIR, uid + ext)
        predicted_path = os.path.join(PREDICTED_DIR, uid + ext)

        s3_client.download_file(S3_BUCKET_NAME, image_name, original_path)

        results = model(original_path, device="cpu")
        annotated_frame = results[0].plot()
        annotated_image = Image.fromarray(annotated_frame)
        annotated_image.save(predicted_path)

        with open(predicted_path, "rb") as f:
            s3_client.upload_fileobj(f, S3_BUCKET_NAME, os.path.basename(predicted_path))

        original_s3_key = image_name  # already the key in S3
        predicted_s3_key = os.path.basename(predicted_path)

        storage.save_prediction(uid, original_s3_key, predicted_s3_key)


        detected_labels = []
        for box in results[0].boxes:
            label_idx = int(box.cls[0].item())
            label = model.names[label_idx]
            score = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            storage.save_detection(uid, label, score, bbox)
            detected_labels.append(label)

        return {
            "prediction_uid": uid,
            "detection_count": len(results[0].boxes),
            "labels": detected_labels
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prediction/{uid}")
def get_prediction_by_uid(uid: str):
    try:
        return storage.get_prediction(uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions/label/{label}")
def get_predictions_by_label(label: str):
    if label not in model.names.values():
        raise HTTPException(status_code=404, detail="Label not found")
    try:
        return storage.get_predictions_by_label(label)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions/score/{min_score}")
def get_predictions_by_score(min_score: float):
    if not (0.0 <= min_score <= 1.0):
        raise HTTPException(status_code=400, detail="Score must be between 0 and 1")
    try:
        return storage.get_predictions_by_score(min_score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/image/{type}/{filename}")
def get_image(type: str, filename: str):
    if type not in ["original", "predicted"]:
        raise HTTPException(status_code=400, detail="Invalid image type")
    path = os.path.join("uploads", type, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)


@app.get("/prediction/{uid}/image")
def get_prediction_image(uid: str, request: Request):
    accept = request.headers.get("accept", "")
    try:
        image_path = storage.get_prediction_image_path(uid)
    except Exception:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Predicted image file not found")

    if "image/png" in accept:
        return FileResponse(image_path, media_type="image/png")
    elif "image/jpeg" in accept or "image/jpg" in accept:
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=406, detail="Client does not accept an image format")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
