#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

from os import listdir
from os.path import exists, isdir

from src.extract_anime_info import get_anime_info
from src.database.episode_info import insert_new_episode, is_in_db, get_ep_id
from src.database.ost_info import insert_new_ost
from src.extract_audio import extract_audio_from_video, create_audio_clip
from src.ost_treatment import episode_processing, recover_ost, get_folder_info

config = ConfigParser()
config.read("nariko.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
extension       = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="process", log_extension=extension)

_EXTENSION = ["avi", "divx", "mkv","mp4"]

def get_all_files(input_dir:str,is_recursive:bool):
    """
        Recover all file from a folder path
            Parameters:
                input_dir       (str): input dir path
                is_recursive   (bool): is the file is recursive
            Returns:
                revelant_files (list):  all video file 
    """
    #TODO test if folder exist and is a dir
    revelant_files = []
    potential_folder = listdir(input_dir)
    length = len(potential_folder)
    for f_id in range(length):
        log.avancement((100 * (f_id+1) / length), after= str(f_id+1)+'/'+str(length) )
        files = potential_folder[f_id]
        path = input_dir + files if input_dir[-1] == '/' else input_dir + '/'+ files
        if isdir(path):
            if is_recursive:
                potential_folder.extend(listdir(path))
        else:
            if is_intersting_file(path):
                revelant_files.append(path)
    print()
    return revelant_files

def is_intersting_file(path):
    """
        Is the folder is an intersting file for nariko processing
            Parameters:
                path  (str): the file path you want to test
            Returns: 
                _    (bool): is the file interesting ?
    """
    extension = str(path).split(".")[-1]
    return extension in _EXTENSION

def process_folder(folder_path:str,is_recursive:bool):
    """
        Process all file from a folder
            Parameters:
                folder_path     (str): input dir path
                is_recursive   (bool): is the file is recursive
    """
    intersting_file = get_all_files(folder_path, is_recursive)
    for video_path in intersting_file:
        _name, _saison, _episode, _isOAV = get_anime_info(video_path)
        in_db, r_code = is_in_db(_name,_saison, _episode)
        if r_code != 200:
            continue
        if in_db:
            log.error("Anime All ready in db")
            continue

        log.info("Process anime : %(name)s saison : %(saison)s episode : %(ep)s" % {"name" : _name, "saison" : _saison, "ep" : _episode})
        log.info("Extracting audio...")
        audio_path, hash_ = extract_audio_from_video(video_path)
        log.done("Extracting audio complete")
        log.info("Create all clip")
        nb_clip, _d, clip_folder = create_audio_clip(audio_path, hash_)
        log.done("Complete")
        log.info("Upload episode in database")
        insert_new_episode(_name, _saison, _episode, _d, hash_,_isOAV)
        _id, r_code = get_ep_id(_name, _saison, _episode)
        log.done("Complete")
        log.done("All clip are created successfully")
        log.info("Recover Data Frame")
        ep_name, duration = get_folder_info(hash_, clip_folder)
        ep_df = episode_processing(clip_folder, duration)
        log.info("Recover OST")
        _OST = recover_ost(ep_df,duration)
        log.done("Complete")
        log.info("Upload ost in database")
        log.debug(_OST)
        for _ost in _OST:
            log.debug(_ost)
            insert_new_ost(_id, _ost["name"], _ost["strat"], _ost["end"])
        
        log.done("Complete")
