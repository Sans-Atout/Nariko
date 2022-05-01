#!/bin/python
from src.extract_audio import extract_audio_from_video, create_audio_clip
from os import listdir
from os.path import exists, isdir
from argparse import ArgumentParser
from json import dump
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
    parser = ArgumentParser(description="Script extract clip from folder")
    parser.add_argument('-f','--folder', type=str, required=False, help="The anime folder")

    args = parser.parse_args()
    video_folder = args.folder

    if not (isdir(video_folder) and exists(video_folder)):
        log.fatal("param is not a folder or did not exist !")

    _JSON = []
    _all_clip = 0
    _path = video_folder if video_folder[-1] == '/' else video_folder+'/'
    all_files = listdir(video_folder)
    log.info("There are %s file in this folder" % len(all_files))

    for _files in all_files:
        log.info("Starting clip file : %s"% _files)
        path, hash_value = extract_audio_from_video(_path+_files)
        nb_clip = create_audio_clip(path, hash_value) + 1
        _all_clip = _all_clip + nb_clip
        _JSON.append({'path' : _files, 'hash' : hash_value, 'clip' : nb_clip})

    log.info("There are %s clips." % _all_clip)
    log.info("Dump JSON into file")
    json_file = open('tmp/output.json','w+')
    dump(_JSON,json_file,indent=4)
    log.done('Done')
