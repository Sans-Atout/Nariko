#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

from os.path import basename
from re import sub, findall, IGNORECASE

config = ConfigParser()
config.read("nariko.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
extension       = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="name", log_extension=extension)

_NUMBER_DETECTOR = [
    "(?:s|v)\d{1,2}ep*(\d{1,2})" ,  # S03EP13
    " - (\d\d(?:\.\d)*) *(?:Fin)* *\[720]" #   // special case
    "\[(\d{1,4}(?:\.\d)*) *(?:END)*]", # [13END]
    "\[(\d{1,4}(?:\.\d)*) *(?:FINAL)*]", # [FINAL]
    "[^\w\d](?:OVA|OAD|SP|OP|ED|NCOP|NCED|EX|CM|PV|Preview|Yokoku|メニュー|Menu|エンディング|Movie)[-_ ]{0,1}(\d{1,2})[^\w\d]", #// [OVA1]
    "「(\d+)」",
    ".+\[(\d{1,4}(?:\.\d)*)[^pPx]{0,4}]", # xxxx[13.5yyyy]xxxx
    "\[(\d{1,4})[ _-].+?]", #xxxx[13-xxxx]xxxx
    "\[[^]+_(\d{1,2})]", # xxxx[xxxx_13]xxxx
    " (\d\d) \[",# xxxx 13 [
    "(?: |\[|]|-)(\d\d)(?:\[|])",# xxxx[ 13[xxxx
    "s\d-(\d{1,2})",# xxxxs2-13xxxx
    "(?:EP|Episode) *(\d{1,4}(?:\.\d\D)*)",# // xxxxEP 13.5xxxx
    "^(\d{1,4}(?:\.\d)*) - ",# 13.5 - xxxx
    " - (\d{1,4}(?:\.\d)*)",# xxxx - 13.5xxxx
    "^(\d{1,4}(?:\.\d)*)\D",# 13.5xxxx
    "(?:#|＃)(\d{1,2})\D",# xxxx#13xxxx
    "(\d{1,4}(?:\.\d)*)[^xpP\]\d]{0,4}",# xxxx 13.5yyyy xxxx
    "(\d{1,4})$",#xxxx13.mp4
    "\D\.(\d{1,3})\.\D",# xxxx.13.xxxx
    "\D(\d{1,4}) - ",# xxxx13 - xxxx
    "(?: |_)(\d{1,3})_",# xxxx_13_xxxx
   
]

_CLEANING_REGEX = {
    "((?:\.mkv)+)$" : "", #Remove file extension
    "[\r\n]$" : "", # remove extra newlines from end of string
    "(v\d)$/i" : "", # remove v2, v3 suffix
    "(\d)v[0-5]/i" : "$1", # remove v2 from 13v2
    "x26(4|5)/i" : "", # remove x264 and x265
    "(\[[0-9a-fA-F]{6,8}])" : "[]", # remove checksum like [c3cafe11]
    "(\[\d{5,}])" : "", # remove dates like [20190301]
    "\(\d+(?:x|X|×)\d+\)" : "", # remove resolutions like (1280x720)
    "(?:1920|1080|1280|720|1024|576)(?:p|P|x|X|×)" : "x", # remove resolutions like 720 or 1080
    "((19|20)\d\d)" : "" # remove years like 1999 or 2019
}

def get_anime_info(file_path:str):
    """
        Recover information from video file
            Parameters:
                file_path  (str): episode file's path

            Returns:
                anime_name (str): anime's name
                saison_nb  (int): saison number
                episode_nb (int): episode number
                is_oav    (bool): is the episode an oav
    """
    
    # Recover file name
    file_name = basename(file_path)
    

def clean_name(ep_name:str):
    """
        cleaning name from a random string
            Parameters:
                ep_name  (str): episode filename
            Returns:
                clean_ep (str): a clean filename
    """
    clean_ep = ep_name
    for _regex, _rep in _CLEANING_REGEX.items():
        clean_ep = sub(_regex,_rep,clean_ep)
    return clean_ep

def get_ep_nb(ep_name:str):
    cleaned_name = clean_name(basename(ep_name))
    for _r in _NUMBER_DETECTOR:
        num = findall(_r,cleaned_name,IGNORECASE) 
        if num != None:
            return float(num[0])
    return None
