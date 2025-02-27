from flask import Blueprint, request, jsonify
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsClassifier

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
    """Recommend workout titles based on user inputs."""
    try:
        encoded_input = {col: label_encoders[col].transform([user_input[col]])[0] for col in features}
        user_category = f"{encoded_input['BodyPart']}_{encoded_input['Type']}"
        user_category_encoded = category_encoder.transform([user_category])[0]

        filtered_data = dataset[dataset["Category"] == user_category_encoded]
        if filtered_data.empty:
            return {"message": "No matches found for the selected BodyPart and Type."}

        encoded_equipment = encoded_input["Equipment"]
        encoded_level = encoded_input["Level"]
        filtered_data = filtered_data[
            (filtered_data["Equipment"] == encoded_equipment) &
            (filtered_data["Level"] == encoded_level)
        ]

        if filtered_data.empty:
            return {"message": "No matches found for the selected Equipment and Level."}

        # Add more exercises if fewer than 7 exist
        if len(filtered_data) < 7:
            body_only_data = dataset[
                (dataset["Equipment"] == label_encoders["Equipment"].transform(["Body Only"])[0]) &
                (dataset["BodyPart"] == encoded_input["BodyPart"]) &
                (dataset["Level"] == encoded_level) &
                (dataset["Type"] == encoded_input["Type"])
            ]
            filtered_data = pd.concat([filtered_data, body_only_data]).drop_duplicates()

        recommended_titles = filtered_data[target].unique()[:7]
        return {"exercises": list(recommended_titles)}

    except Exception as e:
        return {"error": str(e)}


@recommendations_bp.route( '/recommendations', methods=["POST"])
def get_recommendations():
    """API endpoint to get workout recommendations."""
    try:
        user_input = request.json
        recommendations = recommend_titles(user_input)
        return jsonify(recommendations)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
