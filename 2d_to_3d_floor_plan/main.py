import os
from generator import House3DGenerator
from config import DEFAULT_FLOOR_PLAN


def main():
    generator = House3DGenerator()
    floor_plan = DEFAULT_FLOOR_PLAN

    print("=== Enhanced 3D House Generator ===")
    print("Choose generation mode:")
    print("1. Single render")
    print("2. Multiple attempts (recommended)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "2":
        print("→ Generating multiple renders for better accuracy...")
        results = generator.generate_with_multiple_attempts(floor_plan, attempts=3)
        if results:
            print(f"✓ Generated {len(results)} renders")
            saved_files = generator.save_all_results(results)
            print(f"✓ Saved {len(saved_files)} images")
            for _, attempt_name in results:
                print(f"→ {attempt_name}")
        else:
            print("✗ All attempts failed")
    else:
        print("→ Generating single render...")
        if os.path.exists(floor_plan):
            result = generator.generate_from_floorplan(floor_plan)
        else:
            print("⚠️ Floor plan not found, using text-to-image...")
            result = generator.generate_text_to_image()

        if result:
            url = result.get("images", [{}])[0].get("url", "N/A")
            print(f"✓ Render created → {url}")
            generator.save_all_results([(result, "single")])
        else:
            print("✗ Generation failed")


if __name__ == "__main__":
    main()
