import unittest
from fastapi.testclient import TestClient
from app import app  # Make sure this import matches your main app file (app.py)

client = TestClient(app)


class TestYoloAPI(unittest.TestCase):

    def test_predict_endpoint_valid_image(self):
        with open("tests/test_image.jpg", "rb") as image_file:
            response = client.post("/predict", files={"file": image_file})
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction_uid", response.json())

    def test_predict_endpoint_invalid_image(self):
        response = client.post("/predict", files={"file": ("test.txt", b"Not an image file content")})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid image file", response.text)

    def test_predict_endpoint_missing_file(self):
        response = client.post("/predict")
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity
        error_details = response.json()["detail"]
        self.assertTrue(any("Field required" in err["msg"] for err in error_details))

    def test_prediction_details_valid(self):
        with open("tests/test_image.jpg", "rb") as image_file:
            response = client.post("/predict", files={"file": image_file})
        uid = response.json()["prediction_uid"]

        response = client.get(f"/prediction/{uid}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("uid", response.json())
        self.assertEqual(response.json()["uid"], uid)

    def test_prediction_details_invalid(self):
        response = client.get("/prediction/invalid_uid")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Prediction not found", response.text)

    def test_prediction_details_nonexistent(self):
        response = client.get("/prediction/999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Prediction not found", response.text)

    def test_predictions_by_label_existing(self):
        with open("tests/test_image.jpg", "rb") as image_file:
            client.post("/predict", files={"file": image_file})

        response = client.get("/predictions/label/person")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_predictions_by_label_nonexistent(self):
        response = client.get("/predictions/label/nonexistent_label")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Label not found", response.text)

    def test_predictions_by_score_valid(self):
        with open("tests/test_image.jpg", "rb") as image_file:
            client.post("/predict", files={"file": image_file})

        response = client.get("/predictions/score/0.5")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_predictions_by_score_invalid(self):
        response = client.get("/predictions/score/1.5")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Score must be between 0 and 1", response.text)

    def test_prediction_image_valid(self):
        with open("tests/test_image.jpg", "rb") as image_file:
            response = client.post("/predict", files={"file": image_file})
        uid = response.json()["prediction_uid"]

        response = client.get(f"/prediction/{uid}/image", headers={"Accept": "image/png"})
        self.assertEqual(response.status_code, 200)

    def test_prediction_image_invalid(self):
        response = client.get("/prediction/invalid_uid/image", headers={"Accept": "image/png"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("Prediction not found", response.text)

    def test_image_endpoint_original_valid(self):
        with open("tests/test_image.jpg", "rb") as image_file:
            response = client.post("/predict", files={"file": image_file})
        uid = response.json()["prediction_uid"]

        response = client.get(f"/image/original/{uid}.jpg")
        self.assertEqual(response.status_code, 200)


    def test_image_endpoint_predicted_valid(self):
        with open("tests/test_image.jpg", "rb") as image_file:
            response = client.post("/predict", files={"file": image_file})
        uid = response.json()["prediction_uid"]

        response = client.get(f"/image/predicted/{uid}.jpg")
        self.assertEqual(response.status_code, 200)

    def test_image_endpoint_invalid_type(self):
        response = client.get("/image/invalid_type/test.jpg")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid image type", response.text)

    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
