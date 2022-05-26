#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

from os import listdir
from os.path import exists, isdir
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
    #TODO 
    pass