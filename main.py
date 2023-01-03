"""
title: Playlist Program
author: Joanna Hao
date-created: 2023-01-01
"""
from flask import Flask, render_template, request, redirect
from pathlib import Path
import sqlite3

"""
reminders:
- IB naming conventions: uppercase for all variables, camelCase for functions/methods
- 
"""


# ---------- SUBROUTINES ---------- #
# --- INPUTS --- #
def getFileContent(FILENAME):
    FILE = open(FILENAME)
    CONTENT = FILE.readlines()
    FILE.close()
    # cleaning and reformatting data from file
    for i in range(len(CONTENT)):
        if CONTENT[i][-1] == "\n":
            CONTENT[i] = CONTENT[i][:-1]
        CONTENT[i] = CONTENT[i].split(",")
        for j in range(len(CONTENT[i])):
            if CONTENT[i][j].isnumeric():
                CONTENT[i][j] = int(CONTENT[i][j])
    return CONTENT


def menu():
    print("""
Choose an action:
1. View all songs
2. Add a song
3. Modify an existing song's details
4. Remove a song
5. Search songs for potential duplicates
6. Generate a playlist
7. Have the computer guess your favourite artist or genre
    """)
    CHOICE = input("> ")
    if CHOICE.isnumeric() and int(CHOICE) >= 1 and int(CHOICE) <= 7:
        return int(CHOICE)
    else:
        print("Please enter a valid number from the list.")
        return menu()


def getNewSong():
    while True:
        SONG_NAME = input("Name of song? ")
        if SONG_NAME == "":
            print("Please enter a song name.")
            continue
        ARTIST = input("Name of artist? ")
        if ARTIST == "":
            print("Please enter an artist name.")
            continue
        COLLECTION = input("Is it part of an album or EP (1), or is it a single? (2) ")
        if not (COLLECTION.isnumeric() and int(COLLECTION) >= 1 and int(COLLECTION) <= 2):
            print("Please select a valid number.")
            continue
        else:
            if COLLECTION == 1:
                COLLECTION_NAME = input("What is the name of the album or EP? ")
            else:
                COLLECTION_NAME = "single"
        DURATION = input("Duration of song? ")  # expecting X:XX or XX:XX form
        if DURATION.find(":") == -1:
            print("Please enter the duration of the song in the format 'X:XX' or 'XX:XX'.")
            continue
        GENRE = input("What is the genre of the song? Leave the field blank if you are unsure (and fill it in later).")
        break

    NEW_SONG = [SONG_NAME, ARTIST, COLLECTION_NAME, DURATION, GENRE]
    for i in range(len(NEW_SONG)):
        if NEW_SONG[i] == "":
            NEW_SONG[i] = None
    return NEW_SONG



# --- PROCESSING --- #
def setupSongs(DATA_LIST):
    global CURSOR, CONNECTION
    CURSOR.execute("""
        CREATE TABLE
            favourite_songs (
                id INTEGER PRIMARY KEY,
                song_name TEXT NOT NULL,
                artist TEXT NOT NULL,
                collection_name TEXT,
                duration TEXT,
                genre TEXT
            )
    ;""")
    for i in range(1, len(DATA_LIST)):
        CURSOR.execute("""
            INSERT INTO
                favourite_songs
            VALUES (
                ?, ?, ?, ?, ?, ?
            )
        ;""", DATA_LIST[i])
    CONNECTION.commit()


def getAllSongsBasic():
    global CURSOR
    SONGS = CURSOR.execute("""
        SELECT
            song_name,
            artist
        FROM
            favourite_songs
    ;""").fetchall()  # returns a list of tuples

    for i in range(len(SONGS)):
        print(f"{i + 1}. {SONGS[0]} by {SONGS[1]}")  # of the format: 1. (song_name) by (artist)


def insertNewSong(SONG_DETAILS):
    ### worried about inserting list-in-a-list (which would only fill the 1st spot) if [SONG_DETAILS]
    global CURSOR, CONNECTION
    CURSOR.execute("""
        INSERT INTO
            favourite_songs
        VALUES (
            ?, ?, ?, ?, ?, ?
        )
    ;""", SONG_DETAILS)
    CONNECTION.commit()


def getAllSongsComplete():
    # used for: modifying song details
    global CURSOR
    SONGS = CURSOR.execute("""
            SELECT
                song_name,
                artist,
                collection_name,
                duration,
                genre
            FROM
                favourite_songs
        ;""").fetchall()  # returns a list of tuples

    for i in range(len(SONGS)):
        # of the format: 1. song_name by artist on collection_name (duration)
        print(f"{i + 1}. {SONGS[0]} by {SONGS[1]} ", end="")
        if SONGS[2] == "single":
            print(f"({SONGS[3]})")  # just duration
        else:
            print(f"on {SONGS[2]} ({SONGS[3]})")  # print album as well
        if SONGS[-1] != "":
            print(f"Genre: {SONGS[-1]}")
        else:
            print(f"Genre: ?")


def getSongID():
    # used for modifying song details:
    pass


# --- OUTPUTS --- #


# ----- VARIABLES ----- #
DB_NAME = "favourite_songs.db"
FIRST_RUN = True
if (Path.cwd() / DB_NAME).exists():
    FIRST_RUN = False

CONNECTION = sqlite3.connect(DB_NAME)
CURSOR = CONNECTION.cursor()

"""
# --- FLASK --- #
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# app.run(debug=True)  # in main program code section 
"""

if __name__ == "__main__":
    # ----- MAIN PROGRAM CODE ----- #
    if FIRST_RUN:
        CONTENT = getFileContent("filename.ext")  ### MODIFY LATER
        setupSongs(CONTENT)

    while True:
        print("Welcome to your playlist program!")
        # --- inputs
        CHOICE = menu()
        if CHOICE == 2:  # add song
            pass
        elif CHOICE == 3:  # modify song
            pass
        elif CHOICE == 4:  # remove song
            pass
        elif CHOICE == 5:  # duplicates
            pass  # will have 2 inputs to collect
        elif CHOICE == 6:  # generate playlist
            pass
        else:  # guess favourites
            pass

        # --- processing
        if CHOICE == 1:  # see all songs
            pass
        elif CHOICE == 2:  # add song
            pass
        elif CHOICE == 3:  # modify song
            pass
        elif CHOICE == 4:  # remove song
            pass
        elif CHOICE == 5:  # duplicates
            pass
        elif CHOICE == 6:  # generate playlist
            pass
        else:  # guess favourite ____
            pass

        # --- outputs
        if CHOICE == 1:  # see all songs
            pass
        elif CHOICE == 2:  # add song
            pass
        elif CHOICE == 3:  # modify song
            pass
        elif CHOICE == 4:  # remove song
            pass
        elif CHOICE == 5:  # duplicates
            pass
        elif CHOICE == 6:  # generate playlist
            pass
        else:  # guess favourite ____
            pass

"""
Current progress: (2023/01/03)
- finished CHOICE 1, 2
- working on CHOICE 3 

"""