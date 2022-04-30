#!/bin/python
#python librairie for log and argrparse
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger
from argparse import ArgumentParser

#Personnal librairie
from src.dejavu_interface import add_fingerprint
from os.path import exists, isdir

config = ConfigParser()
config.read("nariko.ini")
log_level   = int(config.get("log", "prod_env"))
log_path    = config.get("log", "path")
extension   = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="nariko", log_extension=extension)

if __name__ == '__main__':
    parser = ArgumentParser(description="Script allowing to add to the already seen database the musics of the various animes")
    parser.add_argument('-i','--input', type=str, required=True, help="the musique input folder")
    args = parser.parse_args()
    music_folder = args.input

    if not (exists(music_folder) and isdir(music_folder)):
        log.fatal("Folder does not exist or is not a folder")

    add_fingerprint(music_folder)
