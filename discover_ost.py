#!/bin/python
from src.extract_anime_info import get_anime_info
from src.extract_audio import extract_audio_from_video, create_audio_clip
from src.clean_audio import clean_all_audio
from src.dejavu_interface import test_music
from argparse import ArgumentParser

#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

config = ConfigParser()
config.read("nariko.ini")
log_level   = int(config.get("log", "prod_env"))
log_path    = config.get("log", "path")
extension   = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="nariko", log_extension=extension)
if __name__ == '__main__':
    parser = ArgumentParser(description="Script allowing to add to the already seen database the musics of the various animes")
    parser.add_argument('-i','--input', type=str, required=False, help="the anime input file")

    args = parser.parse_args()
    video_file = args.input
    
