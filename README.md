# Nariko

## Project goal

This project aims to know exactly which OST was played at which time in an anime.

## Open source project used

* [worldveil/dejavu](https://github.com/worldveil/dejavu)
* [tsurumeso/vocal-remover](https://github.com/tsurumeso/vocal-remover/)


## Installation

### Download project file

Here are the commands to run if you want to install this project :
```console
git clone https://github.com/Sans-Atout/Nariko.git
cd Nariko
cp nariko.ini.example nariko.ini
pip install -r requirements.txt
```

## Script explanation

### add_anime_music.py

```shell
./add_anime_music.py -i PATH
```

**PATH** : The folder path where every music could be found

## Create Database

### DejaVu tables

There is no need to create any database for the DejaVu code. The tables used by dejavu are :
```
 Schema |     Name     | Type  |  Owner  
--------+--------------+-------+---------
 public | fingerprints | table |         
 public | songs        | table |         
```

### Project tables
//TODO

## Todo List :

* [ ] Extract anime name from folder or file
* [ ] Save in a database which files are associated with which "hash"
* [x] Extract audio from video file
* [x] Create multiple audio clip
* [x] Clean these audio clip with [vocal-remover](https://github.com/tsurumeso/vocal-remover/)
* [ ] Delete audio files already processed
* [x] Add anime OST fingerprint
* [ ] Extract audio information with [DejaVu code](https://github.com/worldveil/dejavu)
* [ ] Processing of this information to retrieve a chronological list of OSTs with their start and end time stamps
