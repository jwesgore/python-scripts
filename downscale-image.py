"""downscale-image.py

Simple command-line image downscaler using Pillow.

Usage examples:
  python downscale-image.py input.jpg --width 800
  python downscale-image.py input.png --scale 0.5 --output out.png

This preserves aspect ratio when only one of width/height is provided.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Downscale an image while preserving aspect ratio.")
	p.add_argument("input", help="Path to input image file")
	p.add_argument("--output", "-o", help="Path to output file (defaults to input_downscaled.ext)")
	p.add_argument("--width", "-W", type=int, help="Target width in pixels")
	p.add_argument("--height", "-H", type=int, help="Target height in pixels")
	p.add_argument("--scale", "-s", type=float, help="Scale factor (e.g., 0.5 for half size)")
	p.add_argument("--quality", "-q", type=int, default=85, help="JPEG quality (1-95). Ignored for PNG/WebP")
	p.add_argument("--format", "-f", choices=["JPEG", "PNG", "WEBP", "TIFF"], help="Force output format")
	p.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists")
	return p.parse_args()


def compute_target_size(orig: Tuple[int, int], width: Optional[int], height: Optional[int], scale: Optional[float]) -> Tuple[int, int]:
	ow, oh = orig
	if scale is not None:
		if scale <= 0:
			raise ValueError("scale must be > 0")
		return max(1, int(ow * scale)), max(1, int(oh * scale))

	if width is None and height is None:
		# no resizing requested
		return ow, oh

	if width is None:
		# compute width to preserve aspect ratio
		width = max(1, int(ow * (height / oh)))
	elif height is None:
		height = max(1, int(oh * (width / ow)))

	return width, height


def downscale_image(input_path: Path, output_path: Path, target_size: Tuple[int, int], quality: int, out_format: Optional[str]) -> None:
	with Image.open(input_path) as im:
		orig_size = im.size
		if target_size[0] >= orig_size[0] and target_size[1] >= orig_size[1]:
			# no upscaling: save original or copy
			if input_path.resolve() == output_path.resolve():
				return
			im.save(output_path)
			return

		# Use high-quality resampling
		resized = im.resize(target_size, resample=Image.LANCZOS)

		save_kwargs = {}
		fmt = out_format or im.format
		if fmt is None:
			fmt = output_path.suffix.replace(".", "").upper() or im.format or "PNG"

		if fmt.upper() == "JPEG":
			save_kwargs["quality"] = quality
			if resized.mode in ("RGBA", "LA"):
				# JPEG doesn't support alpha; convert to RGB with white background
				bg = Image.new("RGB", resized.size, (255, 255, 255))
				bg.paste(resized, mask=resized.split()[-1])
				resized = bg
		resized.save(output_path, format=fmt, **save_kwargs)


def main() -> None:
	args = parse_args()
	inp = Path(args.input)
	if not inp.exists():
		raise SystemExit(f"Input file not found: {inp}")

	out = Path(args.output) if args.output else inp.with_name(inp.stem + "_downscaled" + inp.suffix)
	if out.exists() and not args.overwrite:
		raise SystemExit(f"Output already exists (use --overwrite): {out}")

	with Image.open(inp) as im:
		target = compute_target_size(im.size, args.width, args.height, args.scale)

	downscale_image(inp, out, target, args.quality, args.format)
	print(f"Saved: {out} ({target[0]}x{target[1]})")


if __name__ == "__main__":
	main()

