#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

# Recover anime information
from os.path import basename
from anitopy import parse

config = ConfigParser()
config.read("nariko.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
extension       = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="name", log_extension=extension)

def get_anime_info(file_path:str):
    """
        Recover information from video file
            Parameters:
                file_path  (str): episode file's path

            Returns:
                anime_name (str): anime's name
                saison_nb  (int): saison number
                episode_nb (int): episode number
                is_oav    (bool): is the episode an oav
    """
    
    file_name = basename(file_path)
    anime_info = parse(file_name)

    anime_name = anime_info["anime_title"] if "anime_title" in anime_info.keys() else file_name
    episode_nb = anime_info["episode_number"] if "episode_number" in anime_info.keys() else 1
    saison_nb = anime_info["anime_season"] if "anime_season" in anime_info.keys() else 1
    _type = anime_info["anime_type"] if "anime_type" in anime_info.keys() else None
    is_oav = _type in ["OAV", "OAD"] or '.' in episode_nb

    return anime_name, float(saison_nb), float(episode_nb), is_oav


