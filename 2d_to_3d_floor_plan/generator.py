import fal_client
from utils import upload_image, preprocess_floorplan, save_image
from config import ENHANCED_PROMPT


class House3DGenerator:
    def __init__(self, model="fal-ai/flux/dev"):
        self.model = model

    def generate_from_floorplan(self, image_path: str, custom_prompt: str | None = None):
        enhanced_image_path = preprocess_floorplan(image_path)
        image_url = upload_image(enhanced_image_path)
        if not image_url:
            return None

        prompt = custom_prompt or ENHANCED_PROMPT
        print("→ Generating 3D architectural render...")
        try:
            return fal_client.run(
                self.model,
                arguments={
                    "prompt": prompt,
                    "image_url": image_url,
                    "strength": 0.55,
                    "num_inference_steps": 50,
                    "guidance_scale": 12.0,
                    "image_size": "landscape_4_3",
                    "seed": 42,
                },
            )
        except Exception as e:
            print(f"✗ Render generation failed: {e}")
            return None

    def generate_with_multiple_attempts(self, image_path: str, custom_prompt: str | None = None, attempts: int = 3):
        results = []
        strength_values = [0.5, 0.55, 0.6]
        guidance_values = [10.0, 12.0, 14.0]

        for i in range(attempts):
            print(f"→ Attempt {i+1}/{attempts}...")
            enhanced_image_path = preprocess_floorplan(image_path)
            image_url = upload_image(enhanced_image_path)
            if not image_url:
                continue

            prompt = custom_prompt or ENHANCED_PROMPT
            try:
                result = fal_client.run(
                    self.model,
                    arguments={
                        "prompt": prompt,
                        "image_url": image_url,
                        "strength": strength_values[i],
                        "num_inference_steps": 50,
                        "guidance_scale": guidance_values[i],
                        "image_size": "landscape_4_3",
                        "seed": 42 + i,
                    },
                )
                results.append((result, f"attempt_{i+1}"))
                print(f"✓ Attempt {i+1} completed")
            except Exception as e:
                print(f"✗ Attempt {i+1} failed: {e}")
        return results

    def generate_text_to_image(self, custom_prompt: str | None = None):
        prompt = custom_prompt or ENHANCED_PROMPT
        print("→ Generating architectural image (text-to-image)...")
        try:
            return fal_client.run(
                self.model,
                arguments={
                    "prompt": prompt,
                    "num_inference_steps": 50,
                    "guidance_scale": 12.0,
                    "image_size": "landscape_4_3",
                },
            )
        except Exception as e:
            print(f"✗ Text-to-image generation failed: {e}")
            return None

    def save_all_results(self, results: list, base_filename: str = "3d_render"):
        saved_files = []
        for i, (result, attempt_name) in enumerate(results):
            filename = f"{base_filename}_{attempt_name}.png"
            saved_file = save_image(result, filename)
            if saved_file:
                saved_files.append(saved_file)
        return saved_files
