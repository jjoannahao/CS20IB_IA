"""
title: Playlist Program
author: Joanna Hao
date-created: 2023-01-01
"""
from flask import Flask, render_template, request, redirect
from pathlib import Path
import sqlite3
from random import randint

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


def getNewSong() -> list:
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


def getModifiedSongDetails(ID):
    global CURSOR
    SONG = CURSOR.execute("""
        SELECT 
            *
        FROM
            favourite_songs
        WHERE
            id = ?
    ;""", [ID]).fetchone()

    print("Leave a field blank if there are no changes to be made.")
    while True:
        SONG_NAME = input(f"Name of song? (currently '{SONG[1]}') ")
        ARTIST = input(f"Name of artist? (currently '{SONG[2]}') ")
        COLLECTION = input(f"Is the song part of an album or EP (y/N)? (currently '{SONG[3]}') ")
        if COLLECTION.lower().strip() == "y" or COLLECTION.lower().strip() == "yes":
            COLLECTION_NAME = input("What is the name of the album or EP? ")
        else:
            COLLECTION_NAME = "single"
        DURATION = input(f"Song duration? (currently '{SONG[4]}') ")
        if DURATION.find(":") == -1:
            print("Please enter a duration in the format 'X:XX' or 'XX:XX'.")
            continue
        GENRE = input(f"What is the genre of the song? (currently '{SONG[-1]}') ")
        break

    return [SONG_NAME, ARTIST, COLLECTION_NAME, DURATION, GENRE]


def getGenerationConditions():
    global TOTAL_SONGS
    while True:
        GENERATION_BASIS = input("Do you want to generate a playlist by artist (1) or genre (2)? ")
        if not (GENERATION_BASIS.isnumeric() and int(GENERATION_BASIS) in (1, 2)):
            print("Please select a valid generation basis from the options.")
            continue
        LENGTH = input(f"How many songs do you want the playlist to generate? (5-{TOTAL_SONGS} or random (R)) ")
        if not (LENGTH.isnumeric() and int(LENGTH) >= 5 and int(LENGTH) <= TOTAL_SONGS or LENGTH.lower().strip() in ("random", "r")):
            print("Please select a valid length or the random option.")
            continue
        elif LENGTH.lower().strip() in ("random", "r"):
            LENGTH = randint(5, TOTAL_SONGS)
        break
    return GENERATION_BASIS, LENGTH


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
        print(f"{i + 1}. {SONGS[i][0]} by {SONGS[i][1]}")  # of the format: 1. (song_name) by (artist)


def insertNewSong(SONG_DETAILS):
    global CURSOR, CONNECTION
    CURSOR.execute("""
        INSERT INTO
            favourite_songs
        VALUES (
            ?, ?, ?, ?, ?, ?
        )
    ;""", SONG_DETAILS)
    CONNECTION.commit()
    return f"{SONG_DETAILS[0]} by {SONG_DETAILS[1]} was successfully added!"


def getAllSongsComplete():
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
        print(f"{i + 1}. {SONGS[i][0]} by {SONGS[i][1]} ", end="")
        if SONGS[2] == "single":
            print(f"({SONGS[i][3]})")  # just duration
        else:
            print(f"on {SONGS[i][2]} ({SONGS[i][3]})")  # print album as well
        if SONGS[-1] != "":
            print(f"Genre: {SONGS[i][-1]}")
        else:
            print(f"Genre: ?")


def getSongID():
    global CURSOR
    SONGS = CURSOR.execute("""
            SELECT
                id,
                song_name,
                artist
            FROM
                favourite_songs
        ;""").fetchall()  # returns a list of tuples

    print("Please select a number:")
    for i in range(len(SONGS)):
        print(f"{i + 1}. {SONGS[i][1]} by {SONGS[i][2]}")

    ROW_INDEX = input("> ")
    if not (ROW_INDEX.isnumeric() and int(ROW_INDEX) >= 1 and int(ROW_INDEX) <= len(SONGS)):
        print("Please enter a valid number from the list.")
        return getSongID()
    else:
        ROW_INDEX = int(ROW_INDEX) - 1
        return SONGS[ROW_INDEX][0]


def updateSongDetails(ID):
    global CURSOR, CONNECTION

    # ------------------------------ original ------------------------------------------------------------ #
    SONG = CURSOR.execute("""
        SELECT 
            *
        FROM
            favourite_songs
        WHERE
            id = ?
    ;""", [ID]).fetchone()
    #
    # print("Leave a field blank if there are no changes to be made.")
    # SONG_DETAILS = []
    # while True:
    #     # --- input
    #     SONG_NAME = input(f"Name of song? (currently '{SONG[1]}') ")
    #     ARTIST = input(f"Name of artist? (currently '{SONG[2]}') ")
    #     COLLECTION = input(f"Is the song part of an album or EP (y/N)? (currently '{SONG[3]}') ")
    #     if COLLECTION.lower().strip() == "y" or COLLECTION.lower().strip() == "yes":
    #         COLLECTION_NAME = input("What is the name of the album or EP? ")
    #     else:
    #         COLLECTION_NAME = "single"
    #     DURATION = input(f"Song duration? (currently '{SONG[4]}') ")
    #     if DURATION.find(":") == -1:
    #         print("Please enter a duration in the format 'X:XX' or 'XX:XX'.")
    #         continue
    #     GENRE = input(f"What is the genre of the song? (currently '{SONG[-1]}') ")
    #     break
    #
    # # --- processing
    # SONG_DETAILS.append(SONG_NAME)
    # SONG_DETAILS.append(ARTIST)
    # SONG_DETAILS.append(COLLECTION_NAME)
    # SONG_DETAILS.append(DURATION)
    # SONG_DETAILS.append(GENRE)
    # ---------------------------------------------------------------------------------------------------- #

    SONG_DETAILS = getModifiedSongDetails(ID)
    for i in range(len(SONG_DETAILS)):
        if SONG_DETAILS[i] == "":
            SONG_DETAILS[i] = SONG[i]

    SONG_DETAILS.append(ID)

    CURSOR.execute("""
        UPDATE
            favourite_songs
        SET
            song_name = ?,
            artist = ?,
            collection_name = ?,
            duration = ?,
            genre = ?
        WHERE
            id = ?
    ;""", SONG_DETAILS)
    CONNECTION.commit()
    return f"{SONG_DETAILS[0]} by {SONG_DETAILS[1]} was successfully updated!"


def deleteSong(ID):
    global CURSOR, CONNECTION
    # retrieve song details for ALERT message
    SONG = CURSOR.execute("""
        SELECT
            song_name,
            artist
        FROM
            favourite_songs
        WHERE
            id = ?
    ;""", [ID]).fetchone()
    # delete song
    CURSOR.execute("""
        DELETE FROM
            favourite_songs
        WHERE
            id = ?
    ;""", [ID])
    CONNECTION.commit()
    return f"{SONG[0]} by {SONG[1]} was successfully deleted!"


def determineTopArtist():
    global CURSOR
    TOP_COUNT, TOP_INDEX = 0, 0
    LISTED_ARTISTS, LISTED_COUNT = [], []  # parallel lists (corresponding indices)
    TOP = []  # list of index/indices of top artists in database
    ARTISTS = CURSOR.execute("""
        SELECT
            id,
            artist
        FROM
            favourite_songs
    ;""").fetchall()

    # count number of songs by each artist
    for i in range(len(ARTISTS)):
        if ARTISTS[i][1] not in LISTED_ARTISTS:
            LISTED_ARTISTS.append(ARTISTS[i][1])
            LISTED_COUNT.append(1)  # represents count of 1 of newly appended genre
        else:
            LISTED_COUNT[i] += 1

    # determine top artist
    for i in range(len(LISTED_COUNT)):
        if LISTED_COUNT > TOP_COUNT:
            TOP_COUNT = LISTED_COUNT

    # check for ties in top artists & retrieve indices of any tied top artists
    if LISTED_COUNT.count(TOP_COUNT) != 1:
        for i in range(len(LISTED_COUNT)):
            if LISTED_COUNT == TOP_COUNT:
                TOP.append(i)
    else:
        TOP = [TOP_COUNT]
    return TOP_COUNT, TOP, LISTED_COUNT


def determineTopGenre():
    global CURSOR
    TOP_COUNT = 0
    LISTED_GENRES, LISTED_COUNT = [], []
    TOP = []  # list of index/indices of top genres in database
    GENRES = CURSOR.execute("""
        SELECT
            id,
            genre
        FROM
            favourite_songs
    ;""").fetchall()

    # count number of songs for each genre
    for i in range(len(GENRES)):
        if GENRES[i][1] not in LISTED_GENRES:
            LISTED_GENRES.append(GENRES[i][1])
            LISTED_COUNT.append(1)  # represents count of 1 of newly appended genre
        else:
            LISTED_COUNT += 1

    # determine top genre
    for i in range(len(LISTED_COUNT)):
        if LISTED_COUNT > TOP_COUNT:
            TOP_COUNT = LISTED_COUNT

    # check for ties in top genre
    if LISTED_COUNT.count(TOP_COUNT) != 1:
        for i in range(len(LISTED_COUNT)):
            if LISTED_COUNT == TOP_COUNT:
                TOP.append(i)
    else:
        TOP = [TOP_COUNT]
    return TOP_COUNT, TOP, LISTED_COUNT


def calculateTopBasisPortion(TOP_COUNT, TOP, PLAYLIST_LENGTH):
    global TOTAL_SONGS
    SONGS_PER_BASIS = []
    TOP_PORTION = int(TOP_COUNT / TOTAL_SONGS)  # floored (rounded down)
    for i in range(len(TOP)):
        SONGS_PER_BASIS.append(PLAYLIST_LENGTH * TOP_PORTION)
    # make SONGS_PER_BASIS parallel to TOP

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

TOTAL_SONGS = 0

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
            NEW_SONG = getNewSong()
        elif CHOICE == 3:  # modify song
            SONG_ID = getSongID()
        elif CHOICE == 4:  # remove song
            SONG_ID = getSongID()

        elif CHOICE == 5:  # duplicates
            GENERATION_BASIS, PLAYLIST_LENGTH = getGenerationConditions()
        elif CHOICE == 6:  # generate playlist
            pass
        else:  # guess favourites
            pass

        # --- processing
        if CHOICE == 2:  # add song
            ALERT = insertNewSong(NEW_SONG)
        elif CHOICE == 3:  # modify song
            ALERT = updateSongDetails(SONG_ID)
        elif CHOICE == 4:  # remove song
            ALERT = deleteSong(SONG_ID)

        elif CHOICE == 5:  # duplicates
            pass
        elif CHOICE == 6:  # generate playlist
            pass
        else:  # guess favourite ____
            pass

        # --- outputs
        # use 'ALERT' variable for all output messages

        if CHOICE == 1:  # see all songs
            getAllSongsBasic()
        elif CHOICE in (2, 3, 4):  # modify song
            print(ALERT)

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