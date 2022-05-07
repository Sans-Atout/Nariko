# Nariko

## Project goal

This project aims to know exactly which OST was played at which time in an anime.

# Installation

## Download project file

Here are the commands to run if you want to install this project :
```console
git clone https://github.com/Sans-Atout/Nariko.git
cd Nariko
cp nariko.ini.example nariko.ini
pip install -r requirements.txt
```

You also need to install ffmpeg software

# Script explanation

## add_anime_music.py

```console
chmod +x add_anime_music.py
./add_anime_music.py -i PATH
```

**PATH** : The folder path where every music could be found

# Database

## DejaVu tables

There is no need to create any database for the DejaVu code. The tables used by dejavu are :
```shell
 Schema |     Name     | Type  |  Owner  
--------+--------------+-------+---------
 public | fingerprints | table |         
 public | songs        | table |         
```


## Anime and Hash association

```shell
|  ID |  Anime  | Saison | Episode |   Hash  | clip_duration | done_at |
+-----+---------+--------+---------+---------+---------------+---------+
| int | varchar |  int   |   int   | varchar |      int      |   int   |
```

## Anime OST Association

```shell
  ID |  anime_id | ost_name | start_time | end_time | done_at |
-----+-----------+----------+------------+----------+---------+
 int |    int    |  varchar |     int    |    int   |   int   |
```

# Todo List :

* [ ] Extract anime name from folder or file
* [ ] Save in a database which files are associated with which "hash" (en cours)
* [x] Extract audio from video file
* [x] Create multiple audio clip
* [x] Delete audio files already processed
* [x] Add anime OST fingerprint
* [x] Extract audio information with [DejaVu code](https://github.com/worldveil/dejavu)
* [ ] Processing of this information to retrieve a chronological list of OSTs with their start and end time stamps

# Some explanations on the project 
## DejaVu result analysis 

Here is an entity representing a result according to our criteria: 
```json
{
	"id" : dejavu_item["song_id"], // int
	"name" : dejavu_item["song_name"], // string
	"detection_accuracy" : dejavu_item["hashes_matched_in_input"] // int
}
```

When retrieving multiple results, the results must be passed as a percentage.

# Open-Source project used

## [worldveil/dejavu](https://github.com/worldveil/dejavu)
