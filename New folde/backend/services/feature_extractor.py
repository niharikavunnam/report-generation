from PIL import Image, ImageStat


def extract_image_features(image_path: str) -> dict:
    image = Image.open(image_path).convert("L")
    stats = ImageStat.Stat(image)

    return {
        "mean_pixel_intensity": float(stats.mean[0]),
        "pixel_std_dev": float(stats.stddev[0]),
        "min_pixel": int(min(image.getdata())),
        "max_pixel": int(max(image.getdata())),
        "shape": [image.height, image.width],
        "bit_depth": "8-bit grayscale",
    }
