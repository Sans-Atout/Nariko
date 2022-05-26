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
type_        = config.get("host_info", "type")

log = Logger(log_path,log_level,service_name="dejavu-interface", log_extension=extension)

CONFIG = {
    "database": {
        "host": host,
        "user": user,
        "password": password,
        "database": db_name,
                },
    "database_type" : type_,
}
log.info("DejaVu object creation...")
djv = Dejavu(CONFIG)
log.done("Object succesfuly created !")

romanji_converter = Cutlet()

fgprint_drop_table = '''DROP TABLE fingerprints;'''
songs_drop_table = '''DROP TABLE songs;'''
fgprint_purge_table = '''TRUNCATE TABLE fingerprints; '''
songs_purge_table = '''TRUNCATE TABLE songs; '''

def add_fingerprint(_path):
    path = _path if _path[-1] == "/" else _path+'/'
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


def start_connexion():
    """
        Database connexion creation
            Returns:
                result (bool): is connexion operationnal
                info (object): connexion and cursor object or error message
    """
    try:
        conn = connect(
              user = username,
              password = password,
              host = host,
              port = port,
              database = db_name
        )
        cur = conn.cursor()
        return {'result' : True, 'info' : (conn, cur)}
    except (Exception, Error) as error:
        log.error(error)
        return {'result' : False, 'info' : str(error)}

def end_connexion(con, cur):
    """
        Close connexion to the database
            Parameters:
                con  (object): PSQL connexion object
                cur  (object): PSQL cursor object
            Returns:
                _ (bool): is connexion ended succesfully
    """
    try:
        cur.close()
        con.close()
        return True
    except Exception as e:
        log.error(e)
        return False

def purge_table():
    """
        Purging the DejaVu table
            Parameters:
            
            Return:
                is_ok  (bool): is insert successfull or not
                r_code  (int): how the function ended

    """
    _ = start_connexion()
    if not _["result"]:
        log.error(_["info"])
        return False, 532
    
    connexion, cursor = _["info"]

    try :
        cursor.execute(fgprint_purge_table)
        cursor.execute(songs_purge_table)
        connexion.commit()
        end_connexion(connexion, cursor)
        return True, 200

    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400

def drop_table():
    """
        Drop the episode_info table
            Parameters:
            
            Return:
                is_ok  (bool): is insert successfull or not
                r_code  (int): how the function ended

    """
    _ = start_connexion()
    if not _["result"]:
        log.error(_["info"])
        return False, 532
    
    connexion, cursor = _["info"]

    try :
        cursor.execute(fgprint_drop_table)
        cursor.execute(songs_drop_table)
        connexion.commit()
        end_connexion(connexion, cursor)
        return True, 200

    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400
