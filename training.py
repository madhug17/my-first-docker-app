import pandas as pd
import joblib
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

# 🔥 Fix tracking path (Windows issue)
mlflow.set_tracking_uri("file:./mlruns")

# 🔥 Set experiment
mlflow.set_experiment("student-performance")

# Load Data
df = pd.read_csv("student-mat.csv", sep=None, engine='python')

# Fix column names
df = df.rename(columns={
    'Medu': 'Mother_edu',
    'Fedu': 'Father_edu',
    'goout': 'Trip'
})

# Target
df["pass"] = (df["G3"] >= 10).astype(int)

# Features
features = [
    "G1", "G2", "absences", "failures", "studytime",
    "Mother_edu", "Father_edu", "Trip", "health",
    "higher", "sex", "school"
]

X = df[features]
y = df["pass"]

# Train-test split (reproducible)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Columns
cat_cols = ["higher", "sex", "school"]
num_cols = [
    "G1", "G2", "absences", "failures", "studytime",
    "Mother_edu", "Father_edu", "Trip", "health"
]

# Preprocessing
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ("num", StandardScaler(), num_cols)
])

# 🔥 Hyperparameters (CHANGE THESE FOR EXPERIMENTS)
n_estimators = 100
max_depth = 4
learning_rate = 0.1

model = XGBClassifier(
    n_estimators=n_estimators,
    max_depth=max_depth,
    learning_rate=learning_rate,
    eval_metric='logloss'
)

pipeline = Pipeline([
    ('preprocess', preprocessor),
    ('model', model)
])

# 🔥 Start MLflow run
with mlflow.start_run():

    # Train
    pipeline.fit(X_train, y_train)

    # Predict
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    # 🔥 Log parameters
    mlflow.log_param("model", "XGBoost")
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("learning_rate", learning_rate)
    mlflow.log_param("features", len(features))

    # 🔥 Log metric
    mlflow.log_metric("accuracy", acc)

    # 🔥 Log + Register model
    mlflow.sklearn.log_model(
        pipeline,
        "model",
        registered_model_name="student-performance-model"
    )

    # Optional local save
    joblib.dump(pipeline, "model.joblib")

    print(f"✅ Accuracy: {acc}")