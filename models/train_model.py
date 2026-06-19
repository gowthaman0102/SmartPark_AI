import pandas as pd
import numpy as np
import ast
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

print("Loading dataset...")

df = pd.read_csv("data/parking_violations.csv")

# ----------------------------
# CLEAN
# ----------------------------

df = df.dropna(
    subset=[
        "junction_name",
        "vehicle_type",
        "violation_type",
        "created_datetime"
    ]
)

df["created_datetime"] = pd.to_datetime(
    df["created_datetime"],
    errors="coerce"
)

df = df.dropna(subset=["created_datetime"])

# ----------------------------
# TIME FEATURES
# ----------------------------

df["hour"] = df["created_datetime"].dt.hour
df["day"] = df["created_datetime"].dt.day
df["month"] = df["created_datetime"].dt.month
df["weekday"] = df["created_datetime"].dt.weekday

df["is_weekend"] = (
    df["weekday"] >= 5
).astype(int)

df["is_peak_hour"] = (
    df["hour"].isin(
        [8, 9, 10, 17, 18, 19]
    )
).astype(int)

# ----------------------------
# CLEAN VIOLATION TYPE
# ----------------------------

def extract_primary_violation(x):

    try:
        v = ast.literal_eval(str(x))

        if isinstance(v, list):
            return str(v[0])

        return str(v)

    except:
        return str(x)

df["primary_violation"] = (
    df["violation_type"]
    .apply(extract_primary_violation)
)

# ----------------------------
# HISTORICAL COUNTS
# ----------------------------

junction_count = (
    df["junction_name"]
    .value_counts()
)

vehicle_count = (
    df["vehicle_type"]
    .value_counts()
)

violation_count = (
    df["primary_violation"]
    .value_counts()
)

df["junction_freq"] = (
    df["junction_name"]
    .map(junction_count)
)

df["vehicle_freq"] = (
    df["vehicle_type"]
    .map(vehicle_count)
)

df["violation_freq"] = (
    df["primary_violation"]
    .map(violation_count)
)

# ----------------------------
# CREATE RISK SCORE
# ----------------------------

df["risk_score"] = (
    0.50 * (
        df["junction_freq"]
        / df["junction_freq"].max()
    )
    +
    0.30 * (
        df["violation_freq"]
        / df["violation_freq"].max()
    )
    +
    0.20 * (
        df["vehicle_freq"]
        / df["vehicle_freq"].max()
    )
)

df["risk_score"] *= 100

# ----------------------------
# ENCODING
# ----------------------------

le_junction = LabelEncoder()
le_vehicle = LabelEncoder()
le_violation = LabelEncoder()

df["junction_encoded"] = (
    le_junction.fit_transform(
        df["junction_name"]
    )
)

df["vehicle_encoded"] = (
    le_vehicle.fit_transform(
        df["vehicle_type"]
    )
)

df["violation_encoded"] = (
    le_violation.fit_transform(
        df["primary_violation"]
    )
)

# ----------------------------
# FEATURES
# ----------------------------

features = [
    "junction_encoded",
    "vehicle_encoded",
    "violation_encoded",
    "hour",
    "day",
    "month",
    "is_weekend",
    "is_peak_hour",
    "junction_freq",
    "vehicle_freq",
    "violation_freq"
]

X = df[features]

y = df["risk_score"]

# ----------------------------
# TRAIN
# ----------------------------

print("Training model...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

score = r2_score(
    y_test,
    pred
)

print(f"R2 Score: {score:.4f}")

# ----------------------------
# SAVE
# ----------------------------

joblib.dump(
    model,
    "models/congestion_model.pkl"
)

joblib.dump(
    le_junction,
    "models/le_junction.pkl"
)

joblib.dump(
    le_vehicle,
    "models/le_vehicle.pkl"
)

joblib.dump(
    le_violation,
    "models/le_violation.pkl"
)

print("Model Saved Successfully")