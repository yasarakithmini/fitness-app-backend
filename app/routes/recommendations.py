from flask import Blueprint, request, jsonify
import pandas as pd
import json
import uuid
import os
import joblib
from app import mysql  # Database connection

recommendations_bp = Blueprint('recommendations', __name__)

# Load pre-trained model and data
model_dir = os.path.join(os.path.dirname(__file__), '../../ml_models')

knn_model = joblib.load(os.path.join(model_dir, "knn_model.pkl"))
label_encoders = joblib.load(os.path.join(model_dir, "label_encoders.pkl"))
category_encoder = joblib.load(os.path.join(model_dir, "category_encoder.pkl"))
dataset = joblib.load(os.path.join(model_dir, "preprocessed_dataset.pkl"))

features = ["Type", "BodyPart", "Equipment", "Level"]
target = "Title"

def recommend_titles(user_input):
    try:
        user_id = user_input.get("user_id")
        if not user_id:
            return {"error": "User ID is required"}

        intensity_change = 0

        # Fetch latest BMI, WHR, and gender
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT bmi, whr, gender FROM user_fitness_records
            WHERE user_id = %s ORDER BY record_date DESC LIMIT 1
        """, (user_id,))
        record = cursor.fetchone()
        cursor.close()

        if record:
            latest_bmi, latest_whr, gender = record
            healthy_bmi = 18.5 <= latest_bmi <= 24.9
            healthy_whr = latest_whr <= (0.90 if gender.lower() == "male" else 0.85)

            if not healthy_bmi or not healthy_whr:
                if latest_bmi < 18.5 or latest_whr < 0.75:
                    intensity_change = -2
                else:
                    intensity_change = -1
        else:
            intensity_change = None

        # Encode input
        encoded_input = [label_encoders[col].transform([user_input[col]])[0] for col in features]
        input_vector = pd.DataFrame([encoded_input], columns=features)

        # Predict category
        predicted_category_encoded = knn_model.predict(input_vector)[0]
        filtered_data = dataset[dataset["Category"] == predicted_category_encoded]

        equipment_encoded = encoded_input[2]
        level_encoded = encoded_input[3]
        filtered_data = filtered_data[
            (filtered_data["Equipment"] == equipment_encoded) &
            (filtered_data["Level"] == level_encoded)
        ]

        if intensity_change == -1:
            filtered_data = filtered_data[
                filtered_data["Level"] != label_encoders["Level"].transform(["Expert"])[0]
            ]
        elif intensity_change == -2:
            filtered_data = filtered_data[
                filtered_data["Level"] == label_encoders["Level"].transform(["Beginner"])[0]
            ]

        if filtered_data.empty or len(filtered_data) < 7:
            fallback_data = dataset[dataset["Category"] == predicted_category_encoded]
            body_only_equipment = label_encoders["Equipment"].transform(["Body Only"])[0]
            fallback_data = fallback_data[
                (fallback_data["Level"] == level_encoded) |
                (fallback_data["Equipment"] == body_only_equipment)
            ]
            filtered_data = pd.concat([filtered_data, fallback_data]).drop_duplicates()

        include_warmup = user_input.get("IncludeWarmupCooldown", "No") == "Yes"
        if filtered_data.empty:
            return {"message": "No matches found for your preferences. Try modifying your input."}

        result = {
            "main": list(filtered_data[target].unique()[:8])
        }

        if include_warmup:
            warmup_data = dataset[dataset["Desc"].str.contains("warm-up", case=False, na=False)]
            cooldown_data = dataset[dataset["Desc"].str.contains("cool-down", case=False, na=False)]
            result["warmup"] = list(warmup_data[target].unique()[:5])
            result["cooldown"] = list(cooldown_data[target].unique()[:5])

        return result

    except Exception as e:
        return {"error": str(e)}


@recommendations_bp.route('/recommendations', methods=["POST"])
def get_recommendations():
    try:
        user_input = request.json
        user_id = user_input.get("user_id")
        bmi = user_input.get("bmi")
        whr = user_input.get("whr")

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        recommendations = recommend_titles(user_input)
        if "error" in recommendations:
            return jsonify(recommendations), 500

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO user_workout_plans (id, user_id, exercises, bmi, whr)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            user_id,
            json.dumps(recommendations),
            bmi,
            whr
        ))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"exercises": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recommendations_bp.route('/workout/latest/<user_id>', methods=['GET'])
def get_latest_workout_plan(user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT exercises FROM user_workout_plans
            WHERE user_id = %s ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        record = cursor.fetchone()
        cursor.close()

        if not record:
            return jsonify({"message": "No previous workout plan found"}), 404

        return jsonify({"exercises": json.loads(record[0])})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
