#!/bin/python
# Log librairy
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

# folder creation librairie
from os import mkdir
from dejavu import Dejavu
from argparse import ArgumentParser

# Log variable initialisation
config = ConfigParser()
config.read("nariko.ini")
log_level   = int(config.get("log", "prod_env"))
log_path    = config.get("log", "path")
extension   = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="initialisation", log_extension=extension)

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
    parser = ArgumentParser(description="Script used to initialize or reset the project")
    parser.add_argument('--reset',action='store_true',required=False, help="reset all the project database")
    args = parser.parse_args()
    _reset = args.reset

    if _reset:

        log.error("Database reset not implemented all ready")
        # TODO : implement reset procedure
    
    log.info("DejaVu database creation")
    djv = Dejavu(CONFIG)
    log.done("DejaVu database succesfuly created")

    log.info("Episode information table creation")

    log.done("Table creation succesfuly created")

    log.info("Project folder creation")
    mkdir("./tmp/audio-clip/")
    mkdir("./tmp/audio-extract/")
    log.done("Project folder created")