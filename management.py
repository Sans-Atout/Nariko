#!/bin/python
# Log librairy
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

# folder creation librairie
from os import mkdir
from os.path import exists
from dejavu import Dejavu
from argparse import ArgumentParser
from shutil import copy 

# database function
from src.database.episode_info import episode_table_creation as ep_create, purge_table as ep_purge, drop_table as ep_drop, dump_db as episode_dump
from src.database.ost_info import ost_table_creation as ost_creation, purge_table as ost_purge, drop_table as ost_drop, dump_db as ost_dump
from src.database.dejavu import drop_table as dv_drop, purge_table as dv_purge

# Log variable initialisation
config = ConfigParser()
config.read("nariko.ini")
log_level   = int(config.get("log", "prod_env"))
log_path    = config.get("log", "path")
extension   = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="management", log_extension=extension)

# Deja vu configuration
db_name     = config.get("database", "db_name")
user        = config.get("database", "name")
password    = config.get("database", "password")
host        = config.get("host_info", "host")
_type       = config.get("host_info", "type")

CONFIG = {
    "database": {
        "host": host,
        "user": user,
        "password": password,
        "database": db_name,
                },
    "database_type" : _type,
}

if __name__ == '__main__':
    parser = ArgumentParser(description="Script used to managhe different asset use in this project")
    parser.add_argument('--reset',action='store_true',required=False, help="reset the project")
    parser.add_argument('--init',action='store_true',required=False, help="initalize the project")
    parser.add_argument('--purge',action='store_true',required=False, help="purge the project")
    parser.add_argument('--dump',action='store_true',required=False, help="dump the database project")

    args = parser.parse_args()
    _reset = args.reset
    _init = args.init
    _purge = args.purge
    _dump = args.dump

    if _purge or _init or _reset:
        if not( (_purge and not _init and not _reset) or (not _purge and _init and not _reset) or (not _purge and not _init and _reset) or _dump):
            log.error("You must specify only one flag")
            log.info("Use --init to initialise project")
            log.info("Use --purge to purge the database")
            log.info("Use --reset to reset project asset")
            exit(-1)

    if _purge:
        log.info("Purge project tables :")
        ep_purge()
        ost_purge()
        log.done("All project specific tables are purge now")
        log.info("Purge DejaVu tables :")
        log.warning("#TODO")
        log.done("All DejaVu tables are purge")
        log.error("Database Purge is not fully implemented")
        # TODO : implement purge procedure
        exit(0)

    if _reset:
        log.info("Reset project tables :")
        # log.warning("table episode_info [1/2] : dropping")
        # ep_drop()
        # log.debug("table episode_info [2/2] : create table")
        # ep_create()
        # log.warning("table ost_info [1/2] : dropping")
        # ost_drop()
        # log.debug("table episode_info [2/2] : create table")
        # ost_creation()

        log.warning("table episode_info [1/2] : dropping")
        dv_drop()
        log.debug("table episode_info [2/2] : create table")
        djv = Dejavu(CONFIG)
        log.done("All tables have been reset")
        exit(0)

    if _init:
        log.info("DejaVu database creation")
        djv = Dejavu(CONFIG)
        log.done("DejaVu database succesfuly created")

        log.info("Episode information table creation")
        ep_create()
        log.done("Table creation succesfuly created")

        log.info("OST information table creation")
        ost_creation()
        log.done("Table creation succesfuly created")


        log.info("Project folder creation")

        if not exists('./tmp/audio-clip/'):
            mkdir("./tmp/audio-clip/")
        else:
            log.warning("The storing clip's folder allready exist")
        if not exists("./tmp/audio-extract/"):
            mkdir("./tmp/audio-extract/")
        else:
            log.warning("The storing audio extract's folder from video allready exist")
        log.done("Project folder created")
        exit(0)

    if _dump:
        log.debug("Dumping episode info table")
        ep_bool , result = episode_dump()
        ost_bool, result = ost_dump()
        log.done("Dumping complete")

        exit(0)



    log.error("No flag used!")
    log.info("Use --init : initialise project")
    log.info("Use --purge : purge the database")
    log.info("Use --reset : reset project asset")
    log.info("Use --dump : dump database into CSV")

    exit(-1)