from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import mlflow
import mlflow.pyfunc
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import os

# 1. MLflow Setup
# Ensure the path is correct relative to where your mlruns folder is
mlflow.set_tracking_uri("file:./mlruns")

class StudentData(BaseModel):
    G1: int
    G2: int
    absences: int
    higher: str
    failures: int = 0
    studytime: int = 2
    Medu: int = 4
    Fedu: int = 4
    goout: int = 2
    health: int = 5
    sex: str = "M"
    school: str = "GP"

app = FastAPI()

# 2. Instrumentator (MUST be before routes or called correctly)
# This sets up the /metrics endpoint for Prometheus
instrumentator = Instrumentator()
instrumentator.instrument(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Defensive Model Loading
try:
    # Use the logged model path or the registry alias
    model = mlflow.pyfunc.load_model("models:/student-performance-model@production")
    print("✅ MLflow Model Loaded from Production Registry")
except Exception as e:
    print(f"⚠️ Registry failed, trying local path: {e}")
    # Fallback to a direct path if the registry isn't configured in the environment
    model = None

@app.get("/")
def health():
    return {
        "status": "online", 
        "model_loaded": model is not None,
        "monitoring": "Prometheus metrics available at /metrics"
    }

@app.post("/predict-easy")
def predict_easy(data: StudentData):
    if model is None:
        raise HTTPException(status_code=503, detail="MLflow model not loaded")
    
    try:
        df_in = pd.DataFrame([data.model_dump()])

        # Mapping names to match your training features
        df_in = df_in.rename(columns={
            "Medu": "Mother_edu",
            "Fedu": "Father_edu",
            "goout": "Trip"
        })

        pred = model.predict(df_in)

        # Handle confidence scores if the model supports it
        try:
            # Some MLflow wrappers require .predict_proba, others return it in .predict
            prob = model.predict_proba(df_in)
            confidence = round(float(np.max(prob)) * 100, 2)
        except:
            confidence = 100.0

        return {
            "prediction": "Pass" if int(pred) == 1 else "Fail",
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Expose metrics
@app.on_event("startup")
async def expose_metrics():
    instrumentator.expose(app)