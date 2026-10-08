from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


SUPPORTED_ARCHITECTURES = {
    "resnet18": "resnet18",
    "densenet121": "densenet121",
    "efficientnet_b0": "efficientnet_b0",
}


def resolve_label(value):
    if value is None:
        return 0
    if isinstance(value, (int, float, bool)):
        return int(bool(value))
    text = str(value).strip().lower()
    if text in {"", "nan", "none", "n/a", "unknown"}:
        return 0
    if text in {"0", "normal", "healthy", "negative", "no finding", "no_finding", "none"}:
        return 0
    if text in {"1", "abnormal", "positive", "disease", "pneumonia", "opacity", "yes", "true"}:
        return 1
    return 1


class ChestXRayDataset(Dataset):
    def __init__(self, rows, image_root: Path, transform=None):
        self.rows = rows
        self.image_root = image_root
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows.iloc[index]
        image_path = self.image_root / row["image_path"] if "image_path" in row else self.image_root / str(row["path"])
        image = Image.open(image_path).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        label = int(resolve_label(row.get("label", row.get("diagnosis", row.get("finding", 0)))))
        return image, torch.tensor(label, dtype=torch.float32)


def _build_model(architecture: str):
    if architecture == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        model.fc = nn.Linear(model.fc.in_features, 1)
    elif architecture == "densenet121":
        model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
        model.classifier = nn.Linear(model.classifier.in_features, 1)
    elif architecture == "efficientnet_b0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, 1)
    else:
        raise ValueError(f"Unsupported architecture: {architecture}")
    return model


def load_rows(dataset_root: Path, csv_path: str | None = None):
    root = Path(dataset_root)
    if csv_path:
        csv_file = Path(csv_path)
    else:
        csv_file = root / "labels.csv"

    if not csv_file.exists():
        raise FileNotFoundError(
            f"No label CSV was found. Expected one of: {csv_file} or {root / 'labels.csv'}. "
            "Example columns: image_path,label or path,label."
        )

    df = pd.read_csv(csv_file)
    if "image_path" not in df.columns and "path" not in df.columns:
        raise ValueError(
            "The dataset CSV must include either 'image_path' or 'path' columns, plus a 'label' or diagnosis column."
        )

    if "label" not in df.columns:
        label_cols = [col for col in df.columns if "label" in col.lower() or "diagn" in col.lower() or "finding" in col.lower()]
        if not label_cols:
            raise ValueError("A label column like 'label', 'diagnosis', or 'finding' is required.")
        df["label"] = df[label_cols[0]]

    if "image_path" not in df.columns:
        df["image_path"] = df["path"]

    df["label"] = df["label"].apply(resolve_label).astype(int)
    return df


def train_model(dataset_path: str, output_model_path: str, architecture: str = "resnet18", epochs: int = 3, batch_size: int = 16, learning_rate: float = 1e-4, csv_path: str | None = None) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    root = Path(dataset_path)
    rows = load_rows(root, csv_path)

    train_df, val_df = train_test_split(rows, test_size=0.2, random_state=42, stratify=rows["label"].astype(int) if "label" in rows.columns else None)
    train_dataset = ChestXRayDataset(train_df, root)
    val_dataset = ChestXRayDataset(val_df, root)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    model = _build_model(architecture).to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    best_loss = float("inf")
    best_path = Path(output_model_path)
    best_path.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, targets in train_loader:
            inputs = inputs.to(device)
            targets = targets.to(device).view(-1, 1)
            optimizer.zero_grad()
            outputs = model(inputs).view(-1, 1)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)

        train_loss = running_loss / len(train_dataset)
        val_loss = 0.0
        correct = 0
        total = 0

        model.eval()
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs = inputs.to(device)
                targets = targets.to(device).view(-1, 1)
                outputs = model(inputs).view(-1, 1)
                loss = criterion(outputs, targets)
                val_loss += loss.item() * inputs.size(0)
                preds = (torch.sigmoid(outputs) >= 0.5).float()
                correct += (preds == targets).sum().item()
                total += targets.numel()

        val_loss = val_loss / len(val_dataset)
        val_accuracy = correct / total if total else 0.0
        print(f"Epoch {epoch + 1}/{epochs} - train_loss={train_loss:.4f} val_loss={val_loss:.4f} val_accuracy={val_accuracy:.4f}")

        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(model.state_dict(), str(best_path))

    return {
        "dataset_path": str(root),
        "output_model_path": str(best_path),
        "architecture": architecture,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "status": "training_complete",
        "best_validation_loss": best_loss,
        "message": "Training completed. Model saved to the trained_models directory.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a chest X-ray classifier for the research project.")
    parser.add_argument("--dataset-root", type=str, required=True, help="Root folder containing images and a labels.csv file.")
    parser.add_argument("--csv-path", type=str, default=None, help="Optional CSV path with image_path and label columns.")
    parser.add_argument("--output-model-path", type=str, default="backend/trained_models/best_model.pth", help="Where to save the trained weights.")
    parser.add_argument("--architecture", type=str, default="resnet18", choices=sorted(SUPPORTED_ARCHITECTURES.keys()), help="CNN architecture to train.")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs.")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size.")
    parser.add_argument("--learning-rate", type=float, default=1e-4, help="Learning rate used by AdamW.")
    args = parser.parse_args()

    result = train_model(
        dataset_path=args.dataset_root,
        output_model_path=args.output_model_path,
        architecture=args.architecture,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        csv_path=args.csv_path,
    )
    print(json.dumps(result, indent=2))
