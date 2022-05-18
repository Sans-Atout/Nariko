#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger

# Source code
from src.extract_anime_info import get_anime_info

# Clip creation libraires
from imageio_ffmpeg import get_ffmpeg_exe
import subprocess as sp
from moviepy.editor import AudioFileClip


# Other external libraires
from random import randint
from hashlib import md5
from os import mkdir

# Log object creation
config = ConfigParser()
config.read("nariko.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
extension       = config.get("log", "extension")
log = Logger(log_path,log_level,service_name="audio", log_extension=extension)

# Audio file extract from an video file
extract_path = "./tmp/audio-extract/extract-%(file_name)s.mp3"
episode_path = "./tmp/audio-clip/%(folder_name)s/"
clip_duration = 20 # clip duration in second

def extract_audio_from_video(video_path:str):
    """
        Extract audio from a video file
            Parameters:
                video_path  (str): video's path where every music clip is situated

            Returns:
                path        (str): path of the music file extracted
                hash_value  (str): hash of the file (custom file hash)
    """
    # create the custom hash
    hash_value = str(md5(video_path.encode()).hexdigest())+get_random_string(10)
    path = extract_path % {'file_name' : hash_value}

    log.info("The hash value for this path is : %s" % hash_value)
    # extract audio from video
    log.info("Extracting audio")
    ffmpeg = get_ffmpeg_exe()

    sp.call([ffmpeg, "-y", "-i", video_path, path], 
                stderr=sp.DEVNULL,
                stdout=sp.DEVNULL
            )


    log.done("File write in %s" % path)

    return path, hash_value

def get_random_string(_LIMIT:int):
    """
        Generated a random string
            Parameters:
                _LIMIT  (int): length of the string randomly generated

            Returns:
                random_string (str): a random string generated
    """
    random_string = ''
    for _ in range(_LIMIT):
        random_integer = randint(97, 97 + 26 - 1)
        flip_bit = randint(0, 1)
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        random_string += (chr(random_integer))
    return random_string

def create_audio_clip(path:str, hash_value:str):
    """
        Create an audio clip
            Parameters:
                _LIMIT  (int): length of the string randomly generated

            Returns:
                random_string (str): a random string generated
    """
    folder_path = episode_path % {'folder_name' : hash_value}
    log.info("Creation of the clip folder")
    mkdir(folder_path)
    log.done("Creation done !")
    clip = AudioFileClip(path)
    duration = int(clip.duration)
    log.info("The misoc duration is : %s" % duration)
    nb_clip = 0
    length = duration-clip_duration
    ffmpeg = get_ffmpeg_exe()
    for i in range(0, duration-clip_duration):
        nb_clip += 1
        log.avancement(100*nb_clip/length, str(nb_clip)+'/'+str(length) )
        sp.run([
                ffmpeg,
                '-ss', str(i),
                '-to', str(i + clip_duration) ,
                '-i', path ,
                f'{folder_path}/audio_clip_{nb_clip}.wav', '-y'
            ],
           stderr=sp.DEVNULL,
           stdout=sp.DEVNULL
           )
    print()
    return nb_clip, folder_path
