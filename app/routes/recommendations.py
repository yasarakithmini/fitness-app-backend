from flask import Blueprint, request, jsonify
import pandas as pd
import json
import uuid
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsClassifier
from app import mysql  # Database connection

recommendations_bp = Blueprint('recommendations', __name__)  # Define Blueprint

# Load the dataset
file_path = "C:/Users/admin/Downloads/archive (11)/megaGymDataset.csv"
dataset = pd.read_csv(file_path)

# Define features and target
features = ["Type", "BodyPart", "Equipment", "Level"]
target = "Title"

# Drop missing target values
dataset = dataset.dropna(subset=[target])

# Handle missing values
imputer = SimpleImputer(strategy="most_frequent")
dataset[features] = imputer.fit_transform(dataset[features])

# Encode categorical features
label_encoders = {col: LabelEncoder() for col in features}
for col in features:
    dataset[col] = label_encoders[col].fit_transform(dataset[col])

# Create category column combining 'BodyPart' and 'Type'
dataset["Category"] = dataset["BodyPart"].astype(str) + "_" + dataset["Type"].astype(str)

# Encode 'Category'
category_encoder = LabelEncoder()
dataset["Category"] = category_encoder.fit_transform(dataset["Category"])

# Train k-NN model
X = dataset[features]
y = dataset["Category"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train, y_train)

def recommend_titles(user_input):
    """Recommend workout titles based on user inputs and BMI/WHR trends."""
    try:
        user_id = user_input.get("user_id")
        if not user_id:
            return {"error": "User ID is required"}

        # Fetch last two fitness records
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT bmi, whr FROM user_fitness_records
            WHERE user_id = %s ORDER BY record_date DESC LIMIT 2
        """, (user_id,))
        records = cursor.fetchall()
        cursor.close()

        # Determine intensity adjustment
        if len(records) < 2:
            intensity_change = 0  # Default to normal intensity
        else:
            prev_bmi, prev_whr = records[1]  # Older record
            latest_bmi, latest_whr = records[0]  # Latest record

            # Adjust intensity based on BMI & WHR trends
            if latest_bmi < prev_bmi and latest_whr < prev_whr:
                intensity_change = 1  # Increase intensity
            elif latest_bmi > prev_bmi and latest_whr > prev_whr:
                intensity_change = -1  # Decrease intensity
            else:
                intensity_change = 0  # Keep normal intensity

        # Encode user inputs
        encoded_input = {col: label_encoders[col].transform([user_input[col]])[0] for col in features}
        user_category = f"{encoded_input['BodyPart']}_{encoded_input['Type']}"
        user_category_encoded = category_encoder.transform([user_category])[0]

        # Filter dataset based on user inputs
        filtered_data = dataset[dataset["Category"] == user_category_encoded]

        # Adjust intensity by filtering "Level"
        if intensity_change == 1:
            filtered_data = filtered_data[filtered_data["Level"] != label_encoders["Level"].transform(["Beginner"])[0]]
        elif intensity_change == -1:
            filtered_data = filtered_data[filtered_data["Level"] != label_encoders["Level"].transform(["Expert"])[0]]

        if filtered_data.empty:
            return {"message": "No matches found"}

        recommended_titles = filtered_data[target].unique()[:7]
        return {"exercises": list(recommended_titles)}

    except Exception as e:
        return {"error": str(e)}

@recommendations_bp.route('/recommendations', methods=["POST"])
def get_recommendations():
    """API endpoint to get and save workout recommendations."""
    try:
        user_input = request.json
        user_id = user_input.get("user_id")
        bmi = user_input.get("bmi")
        whr = user_input.get("whr")

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Get recommended workouts
        recommendations = recommend_titles(user_input)
        if "error" in recommendations:
            return jsonify(recommendations), 500

        exercises = recommendations["exercises"]

        # Save to database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO user_workout_plans (id, user_id, exercises, bmi, whr)
            VALUES (%s, %s, %s, %s, %s)
        """, (str(uuid.uuid4()), user_id, json.dumps(exercises), bmi, whr))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"exercises": exercises})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/workout/latest/<user_id>', methods=['GET'])
def get_latest_workout_plan(user_id):
    """Fetch the latest saved workout plan for the user"""
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
