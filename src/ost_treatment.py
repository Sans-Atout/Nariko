from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer

#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

# External librairies
from os import listdir
from os.path import exists, isdir
from re import findall

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

log = Logger(log_path,log_level,service_name="dejavu-interface", log_extension=extension)


CONFIG = {
    "database": {
        "host": host,
        "user": user,
        "password": password,
        "database": db_name,
                },
    "database_type" : _type,
}
log.info("DejaVu object creation...")
djv = Dejavu(CONFIG)
log.done("Object succesfuly created !")

#song = djv.recognize(FileRecognizer, file)
#log.debug(song)
def treat_folder(folder_path:str, clip_duration:int):
    """
        (param) folder_path string : the folder's path where every music clip is situated
        (param) clip_duration int  : the duration of one clip
    """
    out_confidence = []
    in_confidence = []
    if not isdir(folder_path):
        log.error("The parameter folder_path is not a folder !")
        return {"return_status" : "Error", "result" : "The parameter folder_path is not a folder !"}
    _dir = listdir(folder_path)
    folder_path = folder_path if folder_path[-1] == '/' else folder_path+'/'
    nb_files = len(_dir)
    for file_id in range(nb_files):
        _file = _dir[file_id]
        log.avancement(100*(file_id+1)/nb_files)
        # Get the number of the clip
        clip_number = int(findall('\d+',_file)[0])
        information = recover_information(folder_path+_file, clip_duration,clip_number)
        for item in information:
            out_confidence.append(item["detection_accuracy"])
            #in_confidence.append(item["input_accuracy"])
    print()
    log.debug(min(in_confidence))
    log.debug(max(in_confidence))

    log.debug(min(out_confidence))
    log.debug(max(out_confidence))

    #return in_confidence, out_confidence

def recover_information(file_path:str, clip_duration:int, clip_number:int):
    """
        (param) file_path    string : the path of the music file you want to treat
        (param) clip_duration int  : the duration of one clip
        (param) clip_number   int  : the clip number
    """
    p_song = djv.recognize(FileRecognizer, file_path)
    results = p_song["results"]
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
