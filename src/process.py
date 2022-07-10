#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

from os import listdir, remove
from os.path import exists, isdir
from csv import reader, writer

from src.extract_anime_info import get_anime_info
from src.database.episode_info import insert_new_episode, is_in_db, get_ep_id
from src.database.ost_info import insert_new_ost

from src.database.episode_info import dump_db as episode_dump
from src.database.ost_info import dump_db as ost_dump

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
        log.info("We found %(nb_ost)s OST in this episode" % {"nb_ost": len(_OST)})
        for _ost in _OST:
            log.debug(_ost)
            insert_new_ost(_id, _ost["name"], _ost["strat"], _ost["end"])
        
    log.info("Erase temporary folder")
    #erase_temporary_folder()
    log.done("Complete")

def erase_temporary_folder():
    log.info("Erasing audio clip [1/2]")
    all_extract = listdir("./tmp/audio-clip/")
    for file in all_extract:
        remove("./tmp/audio-clip/"+str(file))
    log.done("Erasing audio clip complete [1/2]")
    log.info("Erasing audio extract [2/2]")
    all_extract = listdir("./tmp/audio-extract/")
    for file in all_extract:
        remove("./tmp/audio-extract/"+str(file))  
    log.done("Erasing audio extract complete [2/2]")


def dumping_all_database():
    log.info("Dumping all database")
    is_ok_ep, episode_dp = episode_dump()
    is_ok_ost, ost_dp = ost_dump()
    log.done("Dumping complete !")
    log.info("We found %(episode_nb)s episode and %(ost_nb)s ost" % {'episode_nb':len(episode_dp), 'ost_nb': len(ost_dp)})
    log.info("Removing duplicates")

    _all_ready_done = []
    ost_remove_dupli = []
    episode_remove_dupli = []

    for episode_ in episode_dp:
        name, saison, episode, clip_d, hash_, timestamp, bool_ = episode_
        if (name, saison, episode) in _all_ready_done:
            log.error("Anime : %(name)s, Saison : %(saison)s, Episode : %(episode)s is duplicate" % {"name" : name, "saison" : saison, "episode" : episode})
            continue
        _all_ready_done.append((name, saison, episode))
        episode_remove_dupli.append(episode_)
        for _ost in ost_dp:
            ep_id, name, start, end, timestamp = _ost
            if ep_id == hash_:
                ost_remove_dupli.append(_ost) 

    log.done("Removing duplicate complete")
    log.info("We found %(episode_nb)s episode and %(ost_nb)s ost" % {'episode_nb':len(episode_remove_dupli), 'ost_nb': len(ost_remove_dupli)})

    log.info("Creating Anime CSV file")
    anime_ = {}
    for name, saison, episode, clip_d, hash_, timestamp, bool_ in episode_remove_dupli:
        if name not in anime_.keys():
            anime_[name] = {}
            anime_[name]["max_episode"] = episode
            anime_[name]["episode_done"] = 1
            anime_[name]["saison"] = saison
        else:
            anime_[name]["max_episode"] = max(anime_[name]["max_episode"], episode)
            anime_[name]["episode_done"] = 1 + anime_[name]["episode_done"]
            anime_[name]["saison"] = max(saison,anime_[name]["saison"])
    log.info("We found %(anime)s anime(s)" % {"anime" : len(anime_)})
    log.info("Creating csv file")

    all_anime   = []
    all_saison  = []

    for name in anime_.keys():
        name_       = name
        max_        = anime_[name]["max_episode"]
        done_       = anime_[name]["episode_done"]
        saison_     = anime_[name]["saison"]
        complete_   = done_ >= saison_*12
        all_anime.append((name_,saison_, int(max_), done_, complete_))
        if saison_ == 1:
            all_saison.append((name_,"Saison %s" % saison_, int(max_), done_))
        else: 
            tmp_saison = {}
            for name, saison, episode, clip_d, hash_, timestamp, bool_ in episode_remove_dupli:
                saison = int(saison)
                if name_ == name:
                    if saison not in tmp_saison.keys():
                        tmp_saison[saison] = {}
                        tmp_saison[saison]["max"]   = episode
                        tmp_saison[saison]["done"]  = 1
                    else:
                        tmp_saison[saison]["max"] = max(episode, tmp_saison[saison]["max"])
                        tmp_saison[saison]["done"]  = 1 + tmp_saison[saison]["done"]
            
            for saison_nb in tmp_saison.keys():
                max_    = tmp_saison[saison_nb]["max"]
                done_   = tmp_saison[saison_nb]["done"]
                all_saison.append((name_,"Saison %s" % saison_nb, int(max_), done_))
    log.done("Complete")

    log.info("Writing in CSV file")

    log.info("[1/4] Anime csv file")
    csv_file = open("./output/anime.csv","w+")
    csv_writer = writer(csv_file)
    csv_writer.writerow(["name", "saison", "max", "done","complete"])
    csv_writer.writerows(all_anime)

    log.info("[2/4] Saison csv file")
    csv_file = open("./output/saison.csv","w+")
    csv_writer = writer(csv_file)
    csv_writer.writerow(["anime", "saison", "episode", "done"])
    csv_writer.writerows(all_saison)

    log.info("[3/4] Episode csv file")
    csv_file = open("./output/episode.csv","w+")
    csv_writer = writer(csv_file)
    csv_writer.writerow(["name", "saison", "episode", "clip", "hash","done_at","is_oav"])
    csv_writer.writerows(episode_remove_dupli)

    log.info("[4/4] OST csv file")
    csv_file = open("./output/ost.csv","w+")
    csv_writer = writer(csv_file)
    csv_writer.writerow(["Episode ID", "Song Name", "start time", "end time", "Done At"])
    csv_writer.writerows(ost_remove_dupli)

    log.done("Writing complete")