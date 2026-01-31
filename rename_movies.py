'''
script for batch renaming movie files and moving them to movies folder
required that yaml and requests libraries are installed, can be installed with pip
required that ffmpeg is installed for conversion, can be installed with winget
'''

import os
import sys
import yaml
import re
import shutil
import subprocess
import requests
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--drive", type=lambda x: x if x.isalpha() and len(x) == 1 else False, default="d")
parser.add_argument("-f", "--folder", type=str, default="")
args, unknownargs = parser.parse_known_args()

drive_letter = args.drive
subfolder = args.folder
                       
extensions = ['.mkv','.mp4','.avi', '.wmv']
convert_if_extension = ['.avi', '.wmv']
convert_to_extension = ".mp4"

def get_movies_folder() -> Path:
    '''Gets the path to place the movies at'''
    movies_folder = Path(f'{drive_letter.capitalize()}:\Movies\{subfolder}')
    if not movies_folder.exists():
        try:
            movies_folder.mkdir()
        except OSError as e:
            raise FileNotFoundError(f"The path '{movies_folder}' does not exist and cannot be created.") from e
    return movies_folder


def plex_update_libraries() -> bool:
    '''atttempt to run "Update Libraries" on Plex'''
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plex_data_path = os.path.join(script_dir, "plex_data.yml")
        with open(plex_data_path) as f:
            plex_data = yaml.load(f, Loader=yaml.FullLoader)
        url = f"{plex_data['plex_address']}/library/sections/1/refresh?X-Plex-Token={plex_data['plex_token']}"
        requests.get(url)
        return True
    except (FileNotFoundError, KeyError, requests.RequestException) as e:
        print(f"Error encountered while updating Plex library: {e}")
        return False
    
def check_title(title:str) -> str:
    '''special checks for errors in title'''
    # check if title has ( at end
    if title[-1] == "(":
        title = title[:-1]
    return title

def convert(movie_path: Path) -> Path:
    '''convert movie to different file format using ffmpeg'''
    try:
        new_file = f"{movie_path.stem}{convert_to_extension}"
        subprocess.run(f'ffmpeg -i "{movie_path.name}" "{new_file}"', cwd=movie_path.parent)
        return movie_path.parent / new_file
    except:
        print("Conversion failed or ffmpeg not installed")
        return movie_path

def input_is_directory(input_folder: Path) -> Path:
    '''search directory for movie file if movie is dir'''
    for extension in extensions:
        search = next(input_folder.glob(f"*{extension}"), None)
        if search:
            return search
    return None
        
def get_subtitle_track(input_file: Path) -> Path | None:
    '''search for subtitle track'''
    return next(input_file.parent.glob("*.srt"), None)
    
def move_movie(arg: Path) -> None:
    # search for movie file and subtitles
    if arg.is_dir():
        movie_file = input_is_directory(arg)
    else:
        movie_file = arg

    subtitle_track = get_subtitle_track(movie_file)

    os.chdir(movie_file.parent)

    # build new movie name
    year_match = re.search(r"\d{4}", movie_file.name)
    if not year_match:
        print(f"Error: No year found in '{movie_file.name}'")
        return
    movie_year = year_match.group(0)
    movie_title = movie_file.name.split(movie_year)[0].replace(".", " ")
    movie_title = check_title(movie_title)
    movie_rename = movie_title + "(" + movie_year + ")" + movie_file.suffix

    # rename file
    movie_file = movie_file.parent / movie_file.rename(movie_rename)

    if subtitle_track:
        subtitle_track = subtitle_track.parent / subtitle_track.rename(movie_file.stem + ".srt")

    # convert file
    if movie_file.suffix in convert_if_extension:
        movie_file = convert(movie_file)
   
    # move file and subtitle track
    try:
        shutil.move(movie_file, movies_folder)

        if subtitle_track:
            shutil.move(subtitle_track, movies_folder)

        # delete parent dir if input is dir
        if arg.is_dir():
            os.chdir(movie_file.parents[1])
            shutil.rmtree(movie_file.parent)
        
        print(f"Done: {movie_file.name}")
    except (OSError, shutil.Error) as e:
        print(f"Problem Moving: {movie_file.name}")
        print(f"\t{e}")

if __name__ == '__main__':
    movies_folder = get_movies_folder()
    for arg in unknownargs:
        move_movie(Path(arg))
    plex_update_libraries()