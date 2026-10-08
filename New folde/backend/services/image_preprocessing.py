from pathlib import Path

from PIL import Image, ImageOps, ImageStat


def preprocess_image(image_path: str) -> dict:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    image = Image.open(path).convert("L")
    image = ImageOps.autocontrast(image)
    image = image.resize((512, 512))
    stats = ImageStat.Stat(image)

    return {
        "source_path": str(path),
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "mean_intensity": float(stats.mean[0]),
        "std_intensity": float(stats.stddev[0]),
        "normalized": True,
        "resized_shape": [image.width, image.height],
    }
