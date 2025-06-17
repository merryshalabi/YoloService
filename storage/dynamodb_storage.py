import boto3
from boto3.dynamodb.conditions import Key
from typing import List, Dict
from storage.base import BaseStorage
import os
import hashlib

class DynamoDBStorage(BaseStorage):
    def __init__(self, table_name: str = None):
        if table_name is None:
            table_name = os.getenv("DYNAMODB_TABLE", "PredictionsDev-merry")
        self.table = boto3.resource("dynamodb",region_name="eu-west-2").Table(table_name)

    def save_prediction(self, uid: str, original_image: str, predicted_image: str) -> None:
        self.table.put_item(Item={
            "PK": f"PRED#{uid}",
            "SK": "META",
            "original_image": original_image,
            "predicted_image": predicted_image
        })

    def save_detection(self, prediction_uid: str, label: str, score: float, box: List[float]) -> None:
        detection_id = hashlib.md5(f"{label}-{score}-{box}".encode()).hexdigest()
        self.table.put_item(Item={
            "PK": f"PRED#{prediction_uid}",
            "SK": f"DETECT#{label}#{detection_id}",
            "label": label,
            "score": score,
            "box": box
        })

    def get_prediction(self, uid: str) -> Dict:
        response = self.table.query(
            KeyConditionExpression=Key("PK").eq(f"PRED#{uid}")
        )
        items = response.get("Items", [])
        if not items:
            raise ValueError("Prediction not found")

        meta = next((item for item in items if item["SK"] == "META"), None)
        if not meta:
            raise ValueError("Prediction metadata not found")

        detections = [
            {
                "label": item["label"],
                "score": item["score"],
                "box": item["box"]
            }
            for item in items if item["SK"].startswith("DETECT#")
        ]

        return {
            "uid": uid,
            "original_image": meta["original_image"],
            "predicted_image": meta["predicted_image"],
            "detection_objects": detections
        }

    def get_predictions_by_label(self, label: str) -> List[Dict]:
        response = self.table.query(
            IndexName="LabelIndex",
            KeyConditionExpression=Key("label").eq(label)
        )
        items = response.get("Items", [])

        predictions = {}
        for item in items:
            if item.get("SK", "").startswith("DETECT#"):
                pred_uid = item["PK"].split("#")[1]
                if pred_uid not in predictions:
                    predictions[pred_uid] = {"uid": pred_uid}

        return list(predictions.values())

    def get_predictions_by_score(self, min_score: float) -> List[Dict]:
        # Full table scan (use GSI in production)
        response = self.table.scan()
        items = response.get("Items", [])

        predictions = {}
        for item in items:
            if item.get("SK", "").startswith("DETECT#") and float(item.get("score", 0)) >= min_score:
                pred_uid = item["PK"].split("#")[1]
                if pred_uid not in predictions:
                    predictions[pred_uid] = {"uid": pred_uid}

        return list(predictions.values())

    def get_prediction_image_path(self, uid: str) -> str:
        response = self.table.get_item(
            Key={"PK": f"PRED#{uid}", "SK": "META"}
        )
        item = response.get("Item")
        if not item:
            raise ValueError("Prediction not found")
        return item["predicted_image"]
