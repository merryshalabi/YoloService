import unittest
from fastapi.testclient import TestClient
from app import app
import boto3
import os

client = TestClient(app)

S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
TEST_IMAGE_NAME = "test_image.jpg"
LOCAL_TEST_IMAGE_PATH = os.path.join("tests", TEST_IMAGE_NAME)


class TestYoloAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        s3 = boto3.client("s3")
        try:
            s3.head_object(Bucket=S3_BUCKET_NAME, Key=TEST_IMAGE_NAME)
        except s3.exceptions.ClientError:
            print("Uploading test image to S3...")
            s3.upload_file(LOCAL_TEST_IMAGE_PATH, S3_BUCKET_NAME, TEST_IMAGE_NAME)

    def test_predict_endpoint_valid_image(self):
        response = client.post("/predict", json={"image_name": TEST_IMAGE_NAME})
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction_uid", response.json())

    def test_predict_endpoint_invalid_image_extension(self):
        response = client.post("/predict", json={"image_name": "invalid_file.txt"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid image file extension", response.text)

    def test_predict_endpoint_missing_image_name(self):
        response = client.post("/predict", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing image_name", response.text)

    def test_predict_image_not_found_in_s3(self):
        response = client.post("/predict", json={"image_name": "nonexistent_image.jpg"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("An error occurred", response.text)

    def test_predict_endpoint_invalid_json_payload(self):
        response = client.post("/predict", data="not a json", headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Expecting value", response.text)

    def test_prediction_details_valid(self):
        response = client.post("/predict", json={"image_name": TEST_IMAGE_NAME})
        uid = response.json()["prediction_uid"]
        response = client.get(f"/prediction/{uid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["uid"], uid)

    def test_prediction_details_invalid(self):
        response = client.get("/prediction/invalid_uid")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Prediction not found", response.text)

    def test_predictions_by_label_existing(self):
        client.post("/predict", json={"image_name": TEST_IMAGE_NAME})
        response = client.get("/predictions/label/person")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_predictions_by_label_nonexistent(self):
        response = client.get("/predictions/label/nonexistent_label")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Label not found", response.text)

    def test_predictions_by_score_valid(self):
        client.post("/predict", json={"image_name": TEST_IMAGE_NAME})
        response = client.get("/predictions/score/0.5")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_predictions_by_score_invalid(self):
        response = client.get("/predictions/score/1.5")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Score must be between 0 and 1", response.text)

    def test_prediction_image_valid(self):
        response = client.post("/predict", json={"image_name": TEST_IMAGE_NAME})
        uid = response.json()["prediction_uid"]
        response = client.get(f"/prediction/{uid}/image", headers={"Accept": "image/png"})
        self.assertEqual(response.status_code, 200)

    def test_prediction_image_invalid(self):
        response = client.get("/prediction/invalid_uid/image", headers={"Accept": "image/png"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("Prediction not found", response.text)

    def test_prediction_image_not_acceptable_format(self):
        response = client.post("/predict", json={"image_name": TEST_IMAGE_NAME})
        uid = response.json()["prediction_uid"]
        response = client.get(f"/prediction/{uid}/image", headers={"Accept": "application/json"})
        self.assertEqual(response.status_code, 406)
        self.assertIn("Client does not accept an image format", response.text)

    def test_image_endpoint_original_valid(self):
        response = client.post("/predict", json={"image_name": TEST_IMAGE_NAME})
        uid = response.json()["prediction_uid"]
        response = client.get(f"/image/original/{uid}.jpg")
        self.assertEqual(response.status_code, 200)

    def test_image_endpoint_predicted_valid(self):
        response = client.post("/predict", json={"image_name": TEST_IMAGE_NAME})
        uid = response.json()["prediction_uid"]
        response = client.get(f"/image/predicted/{uid}.jpg")
        self.assertEqual(response.status_code, 200)

    def test_image_endpoint_invalid_type(self):
        response = client.get("/image/invalid_type/test.jpg")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid image type", response.text)

    def test_get_image_file_not_found(self):
        response = client.get("/image/original/nonexistent.jpg")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Image not found", response.text)

    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
