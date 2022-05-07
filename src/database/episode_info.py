
# SQL command

episode_psql_creation = '''CREATE TABLE episode_info (
                                id SERIAL NOT NULL,
                                anime_name VARCHAR(100) NOT NULL,
                                saison INT NOT NULL ,
                                episode INT NOT NULL ,
                                clip_duration INT NOT NULL ,
                                hash VARCHAR(42) NOT NULL,
                                done_at INT NULL,
                                PRIMARY KEY (id));'''

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
    _ = start_connexion()
    if _["result"]:
        log.info("episode's table creation")
        connexion, cursor = _["info"]
        try :
            cursor.execute(episode_psql_creation)
            connexion.commit()
            log.done("table created ")
            return True
        except (Exception, Error) as error:
            log.error(error)
            nb_error = nb_error +1
            return False