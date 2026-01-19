import os
import re
import argparse
import subprocess
from pydub import AudioSegment
from pydub.utils import which
from tqdm import tqdm

# Ensure pydub uses ffmpeg
AudioSegment.converter = which("ffmpeg")

if not AudioSegment.converter:
    print("❌ ffmpeg not found! Please install ffmpeg and ensure it is in your PATH.")
    exit(1)

def natural_sort(files):
    def key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
    return sorted(files, key=key)

def generate_chapter_metadata(mp3_files, folder_path):
    metadata = [";FFMETADATA1"]
    current_start = 0

    for file in tqdm(mp3_files, desc="📘 Generating chapter metadata"):
        audio = AudioSegment.from_mp3(os.path.join(folder_path, file))
        duration_ms = len(audio)
        end_time = current_start + duration_ms

        metadata.extend([
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            f"START={current_start}",
            f"END={end_time}",
            f"title={os.path.splitext(file)[0]}"
        ])

        current_start = end_time

    metadata_path = os.path.join(folder_path, "chapters.txt")
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write("\n".join(metadata))
    return metadata_path

def create_concat_list(mp3_files, folder_path):
    list_path = os.path.join(folder_path, "concat_list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for file in mp3_files:
            f.write(f"file '{os.path.join(folder_path, file)}'\n")
    return list_path

def merge_mp3s_to_m4b(folder_path, output_filename):
    mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".mp3")]
    if not mp3_files:
        mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".m4a")]
    if not mp3_files:
        print("❌ No MP3 files found.")
        return

    mp3_files = natural_sort(mp3_files)
    print(f"🔊 Found {len(mp3_files)} chapters in: {folder_path}")

    # Create concat list and metadata
    concat_list = create_concat_list(mp3_files, folder_path)
    metadata_file = generate_chapter_metadata(mp3_files, folder_path)

    # Merge audio (ignore image streams)
    temp_audio = os.path.join(folder_path, "temp.m4a")
    merge_cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-map", "0:a", "-c:a", "aac", "-b:a", "64k", temp_audio
    ]
    print("🔧 Merging audio files...")
    subprocess.run(merge_cmd, check=True)

    # Embed chapters
    final_output = os.path.join(folder_path, output_filename)
    embed_cmd = [
        "ffmpeg", "-i", temp_audio, "-i", metadata_file,
        "-map_metadata", "1", "-c", "copy", final_output
    ]
    print("📦 Embedding chapters and exporting M4B...")
    subprocess.run(embed_cmd, check=True)

    # Cleanup
    os.remove(temp_audio)
    os.remove(concat_list)
    print(f"✅ Audiobook created: {final_output}")

def main():
    parser = argparse.ArgumentParser(description="Create a single M4B audiobook from MP3 chapters.")
    parser.add_argument("folder", help="Path to folder containing MP3 files")
    parser.add_argument("-o", "--output", default="audiobook.m4b", help="Output M4B filename")
    args = parser.parse_args()

    merge_mp3s_to_m4b(args.folder, args.output)

if __name__ == "__main__":
    main()
