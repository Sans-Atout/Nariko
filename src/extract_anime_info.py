#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

from os.path import basename


config = ConfigParser()
config.read("init_files/nariko.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
extension       = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="name-extractor", log_extension=extension)

def get_anime_info(file_path):
    log.debug(file_path)
    file_name = basename(file_path)
    log.debug(file_name)
