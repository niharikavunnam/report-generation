from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms


def run_inference(image_path: str, body_region: str, xray_type: str | None = None, model_path: str | None = None) -> dict:
    model_file = model_path or str((Path(__file__).resolve().parent.parent / "trained_models" / "best_model.pth"))
    img = Image.open(image_path).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    tensor = transform(img).unsqueeze(0)

    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, 1)
    state = torch.load(model_file, map_location="cpu")
    model.load_state_dict(state)
    model.eval()

    with torch.no_grad():
        logits = model(tensor)
        prob = torch.sigmoid(logits).item()

    return {
        "image_path": image_path,
        "body_region": body_region,
        "xray_type": xray_type,
        "status": "inference_complete",
        "confidence": round(float(prob), 4),
        "prediction": "probable abnormality present" if prob >= 0.5 else "no abnormality detected",
    }
