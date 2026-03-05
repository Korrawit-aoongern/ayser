import os
from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest


class EvaluateRequest(BaseModel):
    service_id: int
    feature_names: List[str] = Field(min_length=2)
    samples: List[List[float]]
    contamination: float = 0.05
    random_state: int = 42


app = FastAPI(title="Ayser ML Service", version="0.1.0")


@app.get("/")
async def root():
    return {"status": "ok", "service": "Ayser ML Service"}


@app.post("/evaluate")
async def evaluate(request: EvaluateRequest):
    min_samples = int(os.getenv("ML_MIN_SAMPLES", "5"))

    if len(request.feature_names) < 2:
        raise HTTPException(status_code=400, detail="at least two features are required")
    if len(request.samples) < min_samples:
        raise HTTPException(
            status_code=400,
            detail=f"samples must have at least {min_samples} rows",
        )

    feature_count = len(request.feature_names)
    for idx, row in enumerate(request.samples):
        if len(row) != feature_count:
            raise HTTPException(
                status_code=400,
                detail=f"sample at index {idx} has {len(row)} values, expected {feature_count}",
            )

    if request.contamination <= 0 or request.contamination >= 0.5:
        raise HTTPException(status_code=400, detail="contamination must be in (0, 0.5)")

    X = np.asarray(request.samples, dtype=float)
    model = IsolationForest(
        n_estimators=200,
        contamination=request.contamination,
        random_state=request.random_state,
    )
    model.fit(X)

    predictions = model.predict(X)  # 1 normal, -1 anomaly
    scores = model.score_samples(X)  # higher is more normal
    latest_idx = len(X) - 1
    latest_score = float(scores[latest_idx])
    latest_is_anomaly = bool(predictions[latest_idx] == -1)

    means = np.mean(X, axis=0)
    stds = np.std(X, axis=0)
    latest = X[latest_idx]

    top_features = []
    for i, name in enumerate(request.feature_names):
        std = float(stds[i])
        z = 0.0 if std == 0 else float((latest[i] - means[i]) / std)
        top_features.append(
            {
                "name": name,
                "value": float(latest[i]),
                "mean": float(means[i]),
                "zscore": z,
            }
        )

    top_features.sort(key=lambda item: abs(item["zscore"]), reverse=True)

    anomaly_count = int(np.sum(predictions == -1))
    anomaly_ratio = float(anomaly_count / len(predictions))

    return {
        "service_id": request.service_id,
        "model": "IsolationForest",
        "points_used": len(request.samples),
        "features_used": request.feature_names,
        "latest": {
            "is_anomaly": latest_is_anomaly,
            "score": latest_score,
        },
        "anomaly_count": anomaly_count,
        "anomaly_ratio": anomaly_ratio,
        "top_features": top_features[:3],
    }
