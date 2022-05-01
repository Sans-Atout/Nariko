#!/bin/python
#python librairie for log and argrparse
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger
from argparse import ArgumentParser

#Personnal librairie
from src.dejavu_interface import add_fingerprint, add_one_file
from os.path import exists, isdir

config = ConfigParser()
config.read("nariko.ini")
log_level   = int(config.get("log", "prod_env"))
log_path    = config.get("log", "path")
extension   = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="nariko", log_extension=extension)

if __name__ == '__main__':
    parser = ArgumentParser(description="Script allowing to add to the already seen database the musics of the various animes")
    parser.add_argument('-i','--input', type=str, required=False, help="the musique input file")
    parser.add_argument('-f','--folder', type=str, required=False, help="the musique input folder")

    args = parser.parse_args()
    music_folder = args.folder
    music_file = args.input
    if music_file == None and music_folder == None:
        log.error("No file or folder selected")
        log.info("Use -h if you want to have to see help")
    
    if music_folder != None:
        if not (exists(music_folder) and isdir(music_folder)):
            log.fatal("Folder does not exist or is not a folder")
        add_fingerprint(music_folder)
    if music_file != None:
        add_one_file(music_file)
