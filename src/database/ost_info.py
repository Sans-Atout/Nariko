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

#SQL command
ost_psql_creation = '''CREATE TABLE ost_info (
                            id SERIAL NOT NULL,
                            anime_id INT NOT NULL ,
                            ost_name VARCHAR(255) NOT NULL,
                            start_time INT NOT NULL ,
                            end_time INT NOT NULL ,
                            done_at INT NOT NULL,
                            PRIMARY KEY (id));'''

insert_new_ost_psql = ''' INSERT INTO ost_info
                            (anime_id, ost_name,start_time,end_time, done_at) VALUES
                            (%(anime_id)s,%(name)s, %(start)s, %(end)s, %(done_at)s)
                        ;'''

purge_ost_info_table_psql = '''TRUNCATE TABLE ost_info;'''
drop_ost_info_table_psql = '''DROP TABLE ost_info;'''

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

def ost_table_creation():
    """
        Create the OST info table
            Parameters:
                None

            Returns:
                _ (bool): is table succesfully created
    """
    _ = start_connexion()
    if not _["result"]:
        log.error(_["info"])
        return False
    
    log.info("OST table creation")
    connexion, cursor = _["info"]
    try :
        cursor.execute(ost_psql_creation) 
        connexion.commit()
        end_connexion(connexion, cursor)
        log.done("table created ")
        return True
    except (Exception, Error) as error:
        log.error(str(error).replace('\n', ' '))
        return False

def purge_table():
    """
        Purging the ost_info table
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
        cursor.execute(purge_ost_info_table_psql)
        connexion.commit()
        end_connexion(connexion, cursor)
        return True, 200

    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400

def drop_table():
    """
        Drop the ost_info table
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
        cursor.execute(drop_ost_info_table_psql)
        connexion.commit()
        end_connexion(connexion, cursor)
        return True, 200

    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400

def insert_new_ost(anime:int, name:str, start_t:int, end_t:int):
    """
        Insert a new OST into the OST database
            Parameters:
                anime   (int): anime id
                name    (str): OST name
                start_t (int): OST strat time in second
                end_t   (int): OST end time in second
            
            Return:
                is_ok  (bool): is insert successfull or not
                r_code  (int): how the function ended
    """
    if not (type(anime) == int and type(name) == str and type(start_t) == int and type(end_t) == int) :
        log.warning("anime_id : %s, anime name : %s, start time : %s, end time : %s" % (type(anime),type(name),type(start_t), type(end_t)))
        log.error("One of the parameter's type is wrong.")
        return False, 532

    _ = start_connexion()
    if not _["result"]:
        log.error(_["info"])

    connexion, cursor = _["info"]

    try :
        done_at = datetime.timestamp(datetime.now())
        cursor.execute(insert_new_ost_psql, {'name':name,'anime_id' : anime, 'start' : start_t, 'end' : end_t , 'done_at' : done_at})
        connexion.commit()
        end_connexion(connexion, cursor)
        return True, 200
    
    except (Exception, Error) as error:
        log.error(error)
        return False, 400  

