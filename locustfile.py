from locust import HttpUser, task, between
import random
import json

class FitnessUser(HttpUser):
    wait_time = between(1, 3)  # Simulates user think time

    @task
    def get_recommendation(self):
        user_id = random.randint(1, 1000)  # Simulate 1000 different users
        payload = {
            "user_id": f"user{user_id}",
            "Type": "Strength",
            "BodyPart": "Chest",
            "Equipment": "Dumbbell",
            "Level": "Intermediate",
            "bmi": 24.5,
            "whr": 0.85
        }

        self.client.post("/recommendations", json=payload)
