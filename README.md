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

### Create Database

//TODO

## Run program

//TODO

## Known issue

### Issue #0 : incompatibility between the dejavu project and vocal-remover

**P:** Incompatibility of the two projects
**A:** Another project will be set up to process the data extracted via this first project. This project will only serve this purpose and for the moment it has not been decided whether it will also process the extracted data or not 

## Todo List :

* [] Extract anime name from folder or file
* [] Save in a database which files are associated with which "hash"
* [x] Extract audio from video file
* [x] Create multiple audio clip
* [x] Clean these audio clip with [vocal-remover](https://github.com/tsurumeso/vocal-remover/)
* [] Upload of the clean file in a SMB share
* [] Delete audio files already processed
* [] Extract audio information with DejaVu project
* [] Processing of this information to retrieve a chronological list of OSTs with their start and end time stamps
