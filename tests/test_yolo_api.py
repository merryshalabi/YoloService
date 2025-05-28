import unittest
from fastapi.testclient import TestClient
from app import app
import os

client = TestClient(app)

# Replace this with a small valid image for test
LOCAL_TEST_IMAGE_PATH = "tests/test_image.jpg"


class TestYoloAPI(unittest.TestCase):

    def test_predict_endpoint_valid_image(self):
        with open(LOCAL_TEST_IMAGE_PATH, "rb") as f:
            response = client.post("/predict", files={"file": ("test_image.jpg", f, "image/jpeg")})
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction_uid", response.json())

    def test_predict_endpoint_invalid_image_extension(self):
        response = client.post("/predict", files={"file": ("bad.txt", b"fake data", "text/plain")})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid image file", response.text)

    def test_prediction_details_valid(self):
        with open(LOCAL_TEST_IMAGE_PATH, "rb") as f:
            predict_response = client.post("/predict", files={"file": ("test.jpg", f, "image/jpeg")})
        uid = predict_response.json()["prediction_uid"]
        response = client.get(f"/prediction/{uid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["uid"], uid)

    def test_prediction_details_invalid(self):
        response = client.get("/prediction/nonexistent_uid")
        self.assertEqual(response.status_code, 404)

    def test_predictions_by_score_valid(self):
        with open(LOCAL_TEST_IMAGE_PATH, "rb") as f:
            client.post("/predict", files={"file": ("test.jpg", f, "image/jpeg")})
        response = client.get("/predictions/score/0.5")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_predictions_by_score_invalid(self):
        response = client.get("/predictions/score/1.5")
        self.assertEqual(response.status_code, 400)

    def test_get_image_file_not_found(self):
        response = client.get("/image/original/nonexistent.jpg")
        self.assertEqual(response.status_code, 404)

    def test_image_endpoint_invalid_type(self):
        response = client.get("/image/invalid_type/test.jpg")
        self.assertEqual(response.status_code, 400)

    def test_prediction_image_not_acceptable_format(self):
        with open(LOCAL_TEST_IMAGE_PATH, "rb") as f:
            predict_response = client.post("/predict", files={"file": ("test.jpg", f, "image/jpeg")})
        uid = predict_response.json()["prediction_uid"]
        response = client.get(f"/prediction/{uid}/image", headers={"Accept": "application/json"})
        self.assertEqual(response.status_code, 406)

    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
