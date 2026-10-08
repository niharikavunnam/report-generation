def evaluate_model(model_path: str, validation_dataset: str) -> dict:
    return {
        "model_path": model_path,
        "validation_dataset": validation_dataset,
        "accuracy": 0.86,
        "precision": 0.82,
        "recall": 0.8,
        "status": "demo-evaluation-only",
    }
