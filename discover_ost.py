#!/bin/python
from src.extract_audio import extract_audio_from_video, create_audio_clip
from src.ost_treatment import episode_processing, recover_ost, get_folder_info
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
    parser.add_argument('-i','--input', type=str, required=True, help="Anime input file")
    parser.add_argument('-n','--name', type=str, required=True, help="Anime name")
    parser.add_argument('-s','--saison', type=int, required=True, help="Anime saison number")
    parser.add_argument('-e','--episode', type=int, required=True, help="Anime episode number")
    parser.add_argument('--oav', action='store_true',required=False, help="Is the episode an OAV ?")
    args = parser.parse_args()

    # get all arguments
    video_path      = args.input
    anime_name      = args.name
    saison_nb       = int(args.saison)
    episode_nb      = int(args.episode)
    is_oav          = args.oav
    log.info("Process anime : %(name)s saison : %(saison)s episode : %(ep)s" % {"name" : anime_name, "saison" : saison_nb, "ep" : episode_nb})
    log.info("Extracting audio...")
    audio_path, hash_ = extract_audio_from_video(video_path)
    log.done("Extracting audio complete")
    log.info("Create all clip")
    nb_clip, clip_folder = create_audio_clip(audio_path, hash_)
    log.done("All clip are created successfully")
    log.info("Recover Data Frame")
    ep_name, duration = get_folder_info(hash_, clip_folder)
    ep_df = episode_processing(clip_folder, duration)

    OST = recover_ost(ep_df,duration)

    log.done("Processing audio complete")
