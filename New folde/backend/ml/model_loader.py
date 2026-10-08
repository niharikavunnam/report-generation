from pathlib import Path


def load_model(model_name: str = "best_model.pth") -> dict:
    model_path = Path(__file__).resolve().parent.parent / "trained_models" / model_name
    exists = model_path.exists()
    return {
        "name": model_name,
        "status": "loaded" if exists else "not_found",
        "version": "1.0.0",
        "path": str(model_path),
        "description": "Prototype medical imaging model for generalized X-ray assessment.",
    }
