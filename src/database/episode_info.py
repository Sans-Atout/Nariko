
#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

from datetime import datetime
from psycopg2 import connect, Error

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
                                episode_info ( anime_name, saison, episode, clip_duration, hash, done_at ) 
                                VALUES ( %(name)s, %(saison)s, %(episode)s, %(clip_duration)s, %(hash)s, %(done_at)s );'''

purge_episode_table_psql = '''TRUNCATE TABLE episode_info;'''
drop_episode_table_psql = '''DROP TABLE episode_info;'''

is_in_db_psql = ''' SELECT id FROM episode_info WHERE anime_name=%(name)s AND saison=%(saison)s AND episode=%(episode)s ;'''

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
    
def insert_new_episode(name:str,saison:int,episode:int, duration:int, _hash:str):
    """
        Insert a new episode into the episode database
            Parameters:
                name    (str): name of the anime
                saison  (int): saison number
                episode (int): episode number
                duration(int): duration of one clip
                hash    (str): the episode hash
            
            Return:
                is_ok  (bool): is insert successfull or not
                r_code  (int): how the function ended
    """
    if not (type(name) == str and type(saison) == int and type(episode) == int and type(duration)== int and type(_hash) == str) :
        log.warning("name : %s, saison : %s, episode : %s" % (type(name),type(saison),type(episode)))
        log.warning("clip duration : %s, hash : %s" % (type(duration), type(_hash)) )
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
        cursor.execute(insert_new_episode_psql, {'name':name,'saison' : saison, 'episode': episode, 'clip_duration' : duration, 'hash' : _hash, 'done_at' : done_at})
        connexion.commit()
        end_connexion(connexion, cursor)
        return True, 200
    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400  

def is_in_db(name:str,saison:int, episode:int):
    """
        Insert a new episode into the episode database
            Parameters:
                name    (str): name of the anime
                saison  (int): saison number
                episode (int): episode number
            
            Return:
                is_ok  (bool): is insert successfull or not
                r_code  (int): how the function ended

    """
    if not (type(name) == str and type(saison) == int and type(episode) == int) :
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
        is_in_db = cursor.fetchall() == None
        
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
