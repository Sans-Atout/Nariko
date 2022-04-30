from dejavu import Dejavu

#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

#External librairie
from os import listdir, rename
from cutlet import Cutlet

config = ConfigParser()
config.read("nariko.ini")
log_level   = int(config.get("log", "prod_env"))
log_path    = config.get("log", "path")
extension   = config.get("log", "extension")

db_name     = config.get("database", "db_name")
user        = config.get("database", "name")
password    = config.get("database", "password")
host        = config.get("host_info", "host")
type        = config.get("host_info", "type")

log = Logger(log_path,log_level,service_name="dejavu-interface", log_extension=extension)

CONFIG = {
    "database": {
        "host": host,
        "user": user,
        "password": password,
        "database": db_name,
                },
    "database_type" : type,
}
log.info("DejaVu object creation...")
djv = Dejavu(CONFIG)
log.done("Object succesfuly created !")

romanji_converter = Cutlet()

def add_fingerprint(_path):
    path = path if _path[-1] == "/" else _path+'/'
    all_files = listdir(path)
    _l = len(all_files)
    log.info("Add all file to DejaVu")
    for f_id in range(_l):
        romanji_name = romanji_converter.romaji(all_files[f_id])
        old_filename = path + all_files[f_id]
        new_filename = path + romanji_name
        rename(old_filename, new_filename)
        djv.fingerprint_file(file_path=new_filename,song_name=romanji_name)
        log.avancement(100*(f_id+1)/_l, str(f_id+1)+"/"+str(_l))
    print()
    log.done("Rename complete")
    return 0

#def