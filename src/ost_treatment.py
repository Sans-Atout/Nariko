# DejaVu code source
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer

# Python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

# External librairies 
from os import listdir, rename
from os.path import exists, isdir, basename
from re import findall
from pandas import DataFrame
from moviepy.editor import AudioFileClip
from cutlet import Cutlet

# Init file parsing
config = ConfigParser()
config.read("nariko.ini")

log_level   = int(config.get("log", "prod_env"))
log_path    = config.get("log", "path")
extension   = config.get("log", "extension")

db_name     = config.get("database", "db_name")
user        = config.get("database", "name")
password    = config.get("database", "password")
host        = config.get("host_info", "host")
_type        = config.get("host_info", "type")

# DejaVu Dico creation 
CONFIG = {
    "database": {
        "host": host,
        "user": user,
        "password": password,
        "database": db_name,
                },
    "database_type" : _type,
}

# Log object creation
log = Logger(log_path,log_level,service_name="dejavu-interface", log_extension=extension)

# Romanji object creation
log.info("Romanji converter creation")
romanji_converter = Cutlet()
log.done("Romanji converter succesfuly created !")

# Log object creation
log.info("DejaVu object creation...")
djv = Dejavu(CONFIG)
log.done("Object succesfuly created !")

def episode_processing(episode_path:str, clip_duration:int):
    """
        Processes all the clips of a single episode 
            Parameters:
                episode_path  (str): folder's path where every music clip is situated
                clip_duration (int): duration of one clip (in seconds)

            Returns:
                data_frame (DataFrame): dataframe containing all infos of an episode
    """
    if not isdir(episode_path):
        log.error("The parameter episode_path is not a folder !")
        return {"return_status" : "Error", "result" : "The parameter episode_path is not a folder !"}

    all_songs = {}
    _dir = listdir(episode_path)
    log.info(episode_path)
    episode_path = episode_path if episode_path[-1] == '/' else episode_path+'/'
    nb_files = len(_dir)

    for file_id in range(nb_files):
        _file = _dir[file_id]
        log.avancement(100*(file_id+1)/nb_files, str(clip_duration))
        # Get the number of the clip
        clip_number = int(findall('\d+',_file)[0])
        song_found = recover_information(episode_path+_file, clip_duration,clip_number)
        all_songs[clip_number] = song_found
    print()

    log.done("Complete !")
    log.info("Post processing all the data")
    data_frame = post_processing(all_songs)
    log.done("Post processing complete !")

    return data_frame

def recover_information(file_path:str, clip_duration:int, clip_number:int):
    """
        Recover all possibles song for a specific clip
            Parameters:
                file_path     (str): path of the music file you want to treat
                clip_duration (int): duration of one clip (in seconds)
                clip_number   (int): clip number

            Returns:
                _entity       (dict): an entity representing a song and a detection
    """
    results = test_music(file_path)["results"]
    _entity = []
    for r in results:
        _entity.append(
            {
                'id' : r['song_id'],
                'name' : r["song_name"],
                'detection_accuracy' : r['hashes_matched_in_input']
            }
        )
    return _entity

def post_processing(all_song:dict):
    """
        Post processing function that normalize all song result
            Parameters:
                all_song         (dic): all song found by clip number

            Returns:
                data_frame (DataFrame): dataframe containing all infos of an episode
    """

    _length = len(all_song)
    song_keys = list(all_song.keys())

    log.info("Phase 1 : result ponderation")
    for _id in range(_length):
        pourcent = 100 * (_id + 1) / _length
        _max_accuracy = 0
        clip_id = song_keys[_id]
        log.avancement(pourcent, "2/2")
        for _entity in all_song[clip_id]:
            _max_accuracy = _max_accuracy + _entity["detection_accuracy"]

        log.avancement(pourcent, "2/2")
        for _entity in all_song[clip_id]:
            _entity["detection_accuracy"] = 100 * (_entity["detection_accuracy"] / _max_accuracy)
    print()
    
    log.done("Phase 1 : complete")
    log.info("Phase 2 : Creating data array")

    song_score  = []
    song_id     = []
    clips       = []

    for _id in range(_length):
        pourcent = 100 * (_id + 1) / _length
        clip_id = song_keys [_id]
        log.avancement(pourcent)
        for _entity in all_song[clip_id]:
            song_id.append(_entity["name"])
            song_score.append(_entity["detection_accuracy"])
            clips.append(clip_id)

    print()    
    log.done("Phase 2 : Complete")
    log.info("Phase 3 : Creating DataFrame ")

    data_dict = {"clip_id" : clips, "song_id" : song_id, "song_score" : song_score}
    data_Frame = DataFrame(data_dict)

    log.done("Phase 3 : Complete")
    return data_Frame

def get_folder_info(hash:str, path:str):
    """
        Recover some information for a folder
            Parameters:
                hash (str): hash of the folder
                path (str): path of the folder

            Returns:
                episode  (str): episode name
                duration (int): clip duration in seconde
    """

    _file_path = path +'/'+ list(listdir(path))[0]
    clip = AudioFileClip(_file_path)
    duration = int(clip.duration)
    return "One Punch Man, Saison 01 Episode 01", duration

def test_music(_path:str):
    """
        Test music thanks to DejaVu program
            Parameters:
                _path (str) : file path of the music that you want to test
            Returns:
                _    (json) : json object that contains all song recognition
    """
    return djv.recognize(FileRecognizer, _path)

def add_one_file(_path):
    """
        Add music in DejaVu fingerprint database
            Parameters:
                _path (str): file path of the music that you want to add 
            Returns:
                _     (int): nothing
    """
    song_name = basename(_path)
    log.info("File is : %s" % song_name)
    log.info("Insert into DejaVu")
    djv.fingerprint_file(_path, song_name)
    log.done("complete !")
    return 0