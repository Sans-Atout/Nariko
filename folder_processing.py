#!/bin/python
from src.process import process_folder

from argparse import ArgumentParser
from os.path import exists, isdir


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
    parser = ArgumentParser(description="Script to find the OST of each anime episode in a folder")
    parser.add_argument('-i','--input', type=str, required=True, help="Anime input folder")
    parser.add_argument('-r','--recursive',action='store_true',required=False, help="Do you want to recursively process all interesting file")
    args = parser.parse_args()

    video_folder = args.input
    video_folder = video_folder if video_folder[-1] == "/" else video_folder+"/"
    is_recursive = args.recursive

    if not exists(video_folder):
        log.fatal("the folder didn't exist")
    
    if not isdir(video_folder):
        log.fatal("the path given is not the path of a folder")

    process_folder(video_folder, is_recursive)
    