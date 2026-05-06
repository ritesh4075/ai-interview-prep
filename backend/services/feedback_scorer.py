import numpy as np
import os
import pickle

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "feedback_model.pkl")
)

class FeedbackScorer:

    WEIGHTS = {
        "semantic_score": 0.35,
        "keyword_score": 0.25,
        "clarity_score": 0.25,
        "confidence_score": 0.15,
    }

    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Could not load model: {e}")
        return None

    def score(self, evaluation: dict) -> float:
        features = np.array([[
            evaluation.get("semantic_score", 0),
            evaluation.get("keyword_score", 0),
            evaluation.get("clarity_score", 0),
            evaluation.get("confidence_score", 0),
        ]])

        if self.model:
            try:
                raw = self.model.predict(features)[0]
                return round(float(np.clip(raw, 0, 10)), 1)
            except Exception as e:
                print(f"Model prediction error: {e}")

        weighted = sum(
            evaluation.get(k, 0) * w
            for k, w in self.WEIGHTS.items()
        )

        weighted = min(max(weighted, 0), 1)
        return round(weighted * 10, 1)

    def train(self, X: np.ndarray, y: np.ndarray):
        try:
            if X.shape[1] != 4:
                raise ValueError("X must have 4 features")

            import xgboost as xgb

            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42,
            )

            self.model.fit(X, y)

            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

            with open(MODEL_PATH, "wb") as f:
                pickle.dump(self.model, f)

            print(f"Model trained and saved to {MODEL_PATH}")

        except ImportError:
            print("xgboost not installed. Run: pip install xgboost")
        except Exception as e:
            print(f"Training error: {e}")