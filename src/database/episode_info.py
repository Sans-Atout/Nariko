
#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

from datetime import datetime
from psycopg2 import connect, Error
from time import localtime, strftime

config = ConfigParser()
config.read("nariko.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
extension       = config.get("log", "extension")

username = config.get("database", "name")
password = config.get("database", "password")
host     = config.get("host_info", "host")
port     = config.get("host_info", "port")
db_name  = config.get("database", "db_name")

log = Logger(log_path,log_level,service_name="database", log_extension=extension)

# SQL command
episode_psql_creation = '''CREATE TABLE episode_info (
                                id SERIAL NOT NULL,
                                anime_name VARCHAR(100) NOT NULL,
                                saison INT NOT NULL ,
                                episode FLOAT NOT NULL ,
                                clip_duration INT NOT NULL ,
                                hash VARCHAR(42) NOT NULL,
                                done_at INT NULL,
                                is_oav BOOLEAN NOT NULL,
                                PRIMARY KEY (id));'''

insert_new_episode_psql = '''INSERT INTO 
                                episode_info ( anime_name, saison, episode, clip_duration, hash, done_at , is_oav) 
                                VALUES ( %(name)s, %(saison)s, %(episode)s, %(clip_duration)s, %(hash)s, %(done_at)s, %(is_oav)s );'''

purge_episode_table_psql = '''TRUNCATE TABLE episode_info;'''
drop_episode_table_psql = '''DROP TABLE episode_info;'''

is_in_db_psql = ''' SELECT id FROM episode_info WHERE anime_name=%(name)s AND saison=%(saison)s AND episode=%(episode)s ;'''

dump_db_psql = '''SELECT * FROM episode_info;'''
_PATH = "./output/%(timestamp)s_episode.csv"
CSV_HEADER = ["Anime Name", "Saison number", "Episode Number", "Clip duration", "Episode hash", "Done At", "Is OAV"]

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

def episode_table_creation():
    """
        Create the episode table
            Parameters:
                None

            Returns:
                _ (bool): is table succesfully created
    """
    _ = start_connexion()
    if not _["result"]:
        log.error(_["info"])
        return False
    
    log.info("episode's table creation")
    connexion, cursor = _["info"]
    try :
        cursor.execute(episode_psql_creation)
        connexion.commit()
        end_connexion(connexion, cursor)
        log.done("table created ")
        return True
    except (Exception, Error) as error:
        log.error(str(error).replace('\n', ' '))
        return False
    
def insert_new_episode(name:str,saison:float,episode:float, duration:int, _hash:str, is_oav:bool):
    """
        Insert a new episode into the episode database
            Parameters:
                name      (str): name of the anime
                saison  (float): saison number
                episode (float): episode number
                duration  (int): duration of one clip
                hash      (str): the episode hash
            
            Return:
                is_ok  (bool): is insert successfull or not
                r_code  (int): how the function ended
    """
    if not (type(name) == str and type(saison) == float and type(episode) == float and type(duration)== int and type(_hash) == str) and type(is_oav) == bool:
        log.warning("name : %s, saison : %s, episode : %s" % (type(name),type(saison),type(episode)))
        log.warning("clip duration : %s, hash : %s, oav : %s" % (type(duration), type(_hash), type(is_oav)) )
        log.error("One of the parameter's type is wrong.")
        return False, 532
    is_ok, return_code = is_in_db(name,saison, episode)
    if return_code > 300:
        return False, 533
    _ = start_connexion()
    if not _["result"]:
        log.error(_["info"])

    log.info("Insert new episode  : %(hash)s" % {'hash': _hash})
    connexion, cursor = _["info"]

    try :
        done_at = datetime.timestamp(datetime.now())
        cursor.execute(insert_new_episode_psql, {'name':name,'saison' : saison, 'episode': episode, 'clip_duration' : duration, 'hash' : _hash, 'done_at' : done_at, 'is_oav': is_oav})
        connexion.commit()
        end_connexion(connexion, cursor)
        return True, 200
    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400  

def is_in_db(name:str,saison:float, episode:float):
    """
        Insert a new episode into the episode database
            Parameters:
                name      (str): name of the anime
                saison  (float): saison number
                episode (float): episode number
            
            Return:
                is_ok  (bool): is insert successfull or not
                r_code  (int): how the function ended

    """
    if not (type(name) == str and type(saison) == float and type(episode) == float) :
        log.warning("name : %s, saison : %s, episode : %s" % (type(name),type(saison),type(episode)))
        log.error("One of the parameter's type is wrong.")
        return False, 532

    _ = start_connexion()
    if not _["result"]:
        log.error(_["info"])
        return False, 532
    
    log.info("Searching for episode  : %(hash)s" % {'hash':hash(name+str(saison)+str(episode))})
    connexion, cursor = _["info"]

    try :
        cursor.execute(is_in_db_psql, {'name':name,'saison' : saison, 'episode': episode})
        is_in_db = len(cursor.fetchall()) > 0         
        end_connexion(connexion, cursor)
        return is_in_db, 200
    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400

def purge_table():
    """
        Purging the episode_info table
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
        cursor.execute(purge_episode_table_psql)
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
        cursor.execute(drop_episode_table_psql)
        connexion.commit()
        end_connexion(connexion, cursor)
        return True, 200

    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400

def get_ep_id(name:str,saison:float, episode:float):
    """
        Insert a new episode into the episode database
            Parameters:
                name      (str): name of the anime
                saison  (float): saison number
                episode (float): episode number
            
            Return:
                is_ok  (bool): is insert successfull or not
                r_code  (int): how the function ended

    """
    if not (type(name) == str and type(saison) == float and type(episode) == float) :
        log.warning("name : %s, saison : %s, episode : %s" % (type(name),type(saison),type(episode)))
        log.error("One of the parameter's type is wrong.")
        return False, 532

    _ = start_connexion()
    if not _["result"]:
        log.error(_["info"])
        return False, 532
    
    connexion, cursor = _["info"]

    try :
        cursor.execute(is_in_db_psql, {'name':name,'saison' : saison, 'episode': episode})
        anime_id = cursor.fetchall()
        end_connexion(connexion, cursor)
        return anime_id[0][0], 200
    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400

def dump_db():
    """
        Dump episode database
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
        cursor.execute(dump_db_psql)
        all_episode = cursor.fetchall()
        end_connexion(connexion, cursor)
        if len(all_episode) < 0:
            return False, 200
        log.info("Found episode record in database")
        
        all_ep_important_info = []
        for _ep in all_episode:
            try:
                _id, _name, _saison, _ep, _clip_d, _hash, _timestamp, _isOAV = _ep
                all_ep_important_info.append([_name, _saison, _ep, _clip_d, _hash, _timestamp, _isOAV])
            except (Exception, Error) as error:
                pass
        return True, all_ep_important_info
    except (Exception, Error) as error:
        log.error(error)
        return False, 400
