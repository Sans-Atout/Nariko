#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

from os.path import basename


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
    
    # Recover file name
    file_name = basename(file_path)
    