import os
import requests
import base64
from PIL import Image, ImageEnhance
import fal_client
from config import RENDER_DIR


def upload_image(image_path: str) -> str | None:
    """Upload image to fal.ai storage or fallback to base64."""
    if not os.path.exists(image_path):
        print(f"✗ Image path not found: {image_path}")
        return None

    try:
        print("→ Uploading image to fal.ai storage...")
        return fal_client.upload_file(image_path)
    except Exception as e:
        print(f"⚠️ fal upload failed: {e}, trying base64 fallback...")
        try:
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{encoded}"
        except Exception as e2:
            print(f"✗ Base64 fallback failed: {e2}")
            return None


def preprocess_floorplan(image_path: str) -> str:
    """Enhance floor plan image for better AI interpretation."""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        img = ImageEnhance.Contrast(img).enhance(1.3)
        img = ImageEnhance.Sharpness(img).enhance(1.2)

        os.makedirs(RENDER_DIR, exist_ok=True)
        enhanced_filename = os.path.basename(image_path).replace(".png", "_enhanced.png")
        enhanced_path = os.path.join(RENDER_DIR, enhanced_filename)

        img.save(enhanced_path)
        print(f"✓ Enhanced floor plan saved to {enhanced_path}")
        return enhanced_path
    except Exception as e:
        print(f"⚠️ Image preprocessing failed: {e}, using original")
        return image_path


def save_image(result: dict, filename: str) -> str | None:
    """Save generated image to file."""
    try:
        images = result.get("images", [])
        if not images:
            print("✗ No images found in result")
            return None

        url = images[0].get("url")
        if not url:
            print("✗ No valid URL in result")
            return None

        os.makedirs(RENDER_DIR, exist_ok=True)
        full_path = os.path.join(RENDER_DIR, filename)

        response = requests.get(url)
        if response.status_code == 200:
            with open(full_path, "wb") as f:
                f.write(response.content)
            print(f"✓ Saved image to {full_path}")
            return full_path
        else:
            print(f"✗ Failed to download image: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error saving image: {e}")
        return None
