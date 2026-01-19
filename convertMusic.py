import subprocess
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--delete", action="store_true", help="Delete original files after conversion")
args, paths = parser.parse_known_args()

quality = "2"  # MP3 quality scale: 0 (best) to 9 (worst)
supported_extensions = [".flac", ".m4a", ".ogg"]
auto_delete_extensions = [".lrc", ".nfo"]

def convert_song(song_path: Path):
    ext = song_path.suffix.lower()
    if ext in auto_delete_extensions:
        try:
            song_path.unlink()
            print(f"🗑️ Deleted extra file: {song_path}")
        except:
            print(f"⚠️ Error deleting {song_path}: {e}")
    elif ext in supported_extensions:
        output_path = song_path.with_suffix(".mp3")
        command = [
            "ffmpeg",
            "-i", str(song_path),
            "-codec:a", "libmp3lame",
            "-qscale:a", quality,
            str(output_path)
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"🎵 Converted: {song_path} → {output_path}")

        if args.delete:
            try:
                song_path.unlink()
                print(f"🗑️ Deleted original: {song_path}")
            except Exception as e:
                print(f"⚠️ Error deleting {song_path}: {e}")

def process_path(p: Path):
    if p.is_dir():
        for song in p.rglob("*"):
            convert_song(song)
    elif p.is_file():
        convert_song(p)
    else:
        print(f"🚫 {p} is not a valid path")

if __name__ == "__main__":
    for path in paths:
        process_path(Path(path))
