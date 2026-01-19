# Python Scripts Collection

This repository contains several utility scripts for working with images, movies, and audiobooks.

## Scripts

### downscale-image.py
Small utility to downscale images using Pillow.

**Usage examples:**
```bash
python downscale-image.py input.jpg --width 800
python downscale-image.py input.png --scale 0.5 --output out.png
python downscale-image.py input.jpg --height 600 --overwrite
```
- If only one of `--width` or `--height` is provided, the other is calculated to preserve aspect ratio.
- Use `--format` to force output format (JPEG, PNG, WEBP, TIFF).

---

### rename_movies.py
Batch rename and move movie files, with optional conversion to .mp4 and subtitle handling. Also updates Plex libraries if configured.

**Usage:**
```bash
python rename_movies.py -d D -f Subfolder movie_folder_or_file1 [movie_folder_or_file2 ...]
```
- Requires `ffmpeg` installed and available in PATH.
- Optionally updates Plex if `plex_data.yml` is present.

---

### convert-image-type.py
Convert images between formats using Pillow.

**Usage:**
```bash
python convert-image-type.py input.png --format JPEG --output output.jpg
```

---

### combineAudioBookChapters.py
Combine MP3 (or M4A) audiobook chapters into a single M4B file with chapters.

**Usage:**
```bash
python combineAudioBookChapters.py path/to/chapters_folder -o output.m4b
```
- Requires `ffmpeg` installed and available in PATH.
- Will warn and exit if ffmpeg is not found.

---

## Environment Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   ```
2. Activate the environment:
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## .venv and Version Control
- The `.venv` folder is excluded from git via `.gitignore`.
- Do **not** commit your virtual environment; use `requirements.txt` for dependencies.

## Requirements
- See `requirements.txt` for all Python dependencies.
- Some scripts require `ffmpeg` (install via [ffmpeg.org](https://ffmpeg.org/) or your package manager).
