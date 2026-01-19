import argparse
from PIL import Image
import sys
from pathlib import Path

# arg parse stuff
parser = argparse.ArgumentParser(description="Convert images between formats.")

parser.add_argument("--input_file", type=str, help="Path to the input image file.")
parser.add_argument("--input_folder", type=str, help="Path to the input folder containing image files.")
parser.add_argument("--output_format", type=str, required=True, help="Desired output image format (e.g., png, jpg).")
parser.add_argument("--quality", type=int, default=85, help="Quality for output image (applicable for lossy formats like JPEG).")

args = parser.parse_args()
output_format = args.output_format.lower()
quality = args.quality


# validations and stuff
if not args.input_file and not args.input_folder:
    print("Error: You must specify --input_file or --input_folder")
    sys.exit(1)

if args.input_file and args.input_folder:
    print("Error: Specify only one of --input_file or --input_folder")
    sys.exit(1)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

# convert single image file
def convert_image(input_path: Path):
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return

    output_path = input_path.with_suffix(f".{output_format}")

    try:
        with Image.open(input_path) as img:
            # convert to RGB for formats that don't support alpha
            if output_format in {"jpg", "jpeg"} and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            save_kwargs = {}
            if output_format in {"jpg", "jpeg", "webp"}:
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True

            img.save(output_path, format=output_format.upper(), **save_kwargs)
            print(f"Converted: {input_path.name} → {output_path.name}")

    except Exception as e:
        print(f"Failed to convert {input_path}: {e}")

# process for a single image file
if args.input_file:
    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    convert_image(input_path)

# process for a folder of images
if args.input_folder:
    folder_path = Path(args.input_folder)

    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Invalid folder: {folder_path}")
        sys.exit(1)

    for image_path in folder_path.iterdir():
        if image_path.is_file():
            convert_image(image_path)
