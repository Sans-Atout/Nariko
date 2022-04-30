#python librairie for log
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger
from src.extract_anime_info import get_anime_info
from random import randint
from hashlib import md5

from os import mkdir
from moviepy.editor import VideoFileClip, AudioFileClip

#Create subclip
from imageio_ffmpeg import get_ffmpeg_exe
import subprocess as sp

config = ConfigParser()
config.read("nariko.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
extension       = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="extract-audio", log_extension=extension)

base_path = "./tmp/audio-extract/extract-%(file_name)s.mp3"
clip_duration = 11

def extract_audio_from_video(video_path):
    hash_value = str(md5(video_path.encode()).hexdigest())+get_random_string(10)
    path = base_path % {'file_name' : hash_value}
    log.info("The hash value for this path is : %s" % hash_value)
    videoclip=VideoFileClip(video_path)
    audioclip=videoclip.audio
    audioclip.write_audiofile(path)
    audioclip.close()
    videoclip.close()
    log.done("File write in %s" % path)
    return path, hash_value

def get_random_string(_LIMIT):
    random_string = ''
    for _ in range(_LIMIT):
        random_integer = randint(97, 97 + 26 - 1)
        flip_bit = randint(0, 1)
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        random_string += (chr(random_integer))
    return random_string

def create_audio_clip(path, hash_value):
    log.info("Creation of the clip folder")
    folder_path = "tmp/audio-clip/"+str(hash_value)
    mkdir(folder_path)
    log.done("Creation done !")
    clip = AudioFileClip(path)
    duration = int(clip.duration)
    log.info("The clip duration is : %s" % duration)
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
    return nb_clip
