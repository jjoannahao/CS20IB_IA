"""
title: Playlist Program
author: Joanna Hao
date-created: 2023-01-01
"""
from pathlib import Path
import sqlite3
from random import randint
import sys

"""
reminders:
- IB naming conventions: uppercase for all variables, camelCase for functions/methods
- have the triple line comments for all functions 
"""


# -------------------- SUBROUTINES -------------------- #
# --- INPUTS --- #
def getFileContent(FILENAME):
    """
    extract and cleanse data so when returned, it can be inputted into a database.
    :param FILENAME: str
    :return: list
    """
    FILE = open(FILENAME)
    CONTENT = FILE.readlines()
    FILE.close()
    # cleaning and reformatting data from file
    for i in range(len(CONTENT)):
        if CONTENT[i][-1] == "\n":
            CONTENT[i] = CONTENT[i][:-1]
        CONTENT[i] = CONTENT[i].split(",")  # now a list
        for j in range(len(CONTENT[i])):  # checking items in list
            if CONTENT[i][j].isnumeric():
                CONTENT[i][j] = int(CONTENT[i][j])
            elif CONTENT[i][j] == "":
                CONTENT[i][j] = None
            elif CONTENT[i][j][0] == "'" and CONTENT[i][j][-1] == "'":
                CONTENT[i][j][0] = ""
                CONTENT[i][j][0] = ""
    return CONTENT


def menu():
    """
    display options for how user can interact with program
    :return: int
    """
    print("""
Choose an action:
1. View all songs
2. Add a song
3. Modify an existing song's details
4. Remove a song
5. Search songs for potential duplicates
6. Generate a playlist
7. Have the computer guess your favourite artist or genre
8. Exit
    """)
    CHOICE = input("> ")
    if CHOICE.isnumeric() and int(CHOICE) >= 1 and int(CHOICE) <= 8:
        return int(CHOICE)
    else:
        print("Please enter a valid number from the list.")
        return menu()


def getNewSong() -> list:
    """
    get new song's name, artist, collection name or whether it's a single, duration, and genre
    :return: list
    """
    while True:
        SONG_NAME = input("Name of song? ")
        if SONG_NAME == "":
            print(">> Please enter a song name.")
            continue
        break

    while True:
        ARTIST = input("Name of artist? ")
        if ARTIST == "":
            print(">> Please enter an artist name.")
            continue
        break

    while True:
        COLLECTION = input("Is it part of an album or EP (1), or is it a single? (2) ")
        if not (COLLECTION.isnumeric() and int(COLLECTION) >= 1 and int(COLLECTION) <= 2):
            print(">> Please select a valid number.")
            continue
        else:
            if COLLECTION == "1":
                COLLECTION_NAME = input("What is the name of the album or EP? ")
                if COLLECTION_NAME == "":
                    print(">> Please enter an album/EP name.")
                    continue
            else:
                COLLECTION_NAME = "Single"
        break

    while True:
        DURATION = input("Duration of song? ('XX:XX' format) ")
        if not (DURATION.find(":") == 2 and len(DURATION) == 5 and DURATION[0].isnumeric() and DURATION[1].isnumeric() and DURATION[-1].isnumeric() and DURATION[-2].isnumeric()):
            print(">> Please enter the duration of the song in the format 'XX:XX' where X represent numbers.")
            continue
        break

    while True:
        GENRE = input("What is the genre of the song? ")
        if GENRE == "":
            print(">> Please enter a genre.")
            continue
        break

    NEW_SONG = [SONG_NAME, ARTIST, COLLECTION_NAME, DURATION, GENRE]
    for i in range(len(NEW_SONG)):
        if NEW_SONG[i] == "":
            NEW_SONG[i] = None
    return NEW_SONG


def getModifiedSongDetails(ID):
    """
    determine updated detail(s) about song's name, artist, collection name or whether it's a single, duration, and genre
    :param ID: int (id of song in database)
    :return: list
    """
    global CURSOR
    SONG = CURSOR.execute("""
        SELECT 
            *
        FROM
            songs
        WHERE
            id = ?
    ;""", [ID]).fetchone()

    print("Leave a field blank if there are no changes to be made.")
    while True:
        SONG_NAME = input(f"Name of song? (currently '{SONG[1]}') ")
        ARTIST = input(f"Name of artist? (currently '{SONG[2]}') ")
        COLLECTION = input("Is the song part of an album or EP (y/N)? ")
        if COLLECTION.lower().strip() == "y" or COLLECTION.lower().strip() == "yes":
            COLLECTION_NAME = input(f"What is the name of the album or EP? (currently '{SONG[3]}') ")
            if COLLECTION_NAME == "":
                print(">> Please enter an album/EP name.")
                continue
        else:
            COLLECTION_NAME = "single"
        DURATION = input(f"Song duration? (currently '{SONG[4]}') ")
        if not DURATION == "" and not (DURATION.find(":") == 2 and len(DURATION) == 5):
            print(">> Please enter a duration in the format 'XX:XX'.")
            continue
        GENRE = input(f"What is the genre of the song? (currently '{SONG[-1]}') ")
        break
    print(f"new details: {[SONG_NAME, ARTIST, COLLECTION_NAME, DURATION, GENRE]}")
    return [SONG_NAME, ARTIST, COLLECTION_NAME, DURATION, GENRE]


def getGenerationBasis():
    """
    determine whether to guess user's favourite artist or genre
    :return: int
    """
    global CHOICE
    while True:
        GENERATION_BASIS = input("Do you want the program to guess your favourite artist (1) or genre (2)? ")
        if not (GENERATION_BASIS.isnumeric() and int(GENERATION_BASIS) in (1, 2)):
            print("Please select a valid generation basis from the options.")
            continue
        break
    return int(GENERATION_BASIS)


def getPlaylistLength():
    """
    determine length of playlist user wants to generate
    :return: int
    """
    global randint
    TOTAL_SONGS = determineTotalSongs()
    while True:
        LENGTH = input(f"How many songs do you want the program to generate? (1-{TOTAL_SONGS} or random (R)) ")
        if not (LENGTH.isnumeric() and int(LENGTH) >= 1 and int(LENGTH) <= TOTAL_SONGS or LENGTH.lower().strip() in (
        "random", "r")):
            print("Please select a valid length or the 'random' option.")
            continue
        elif LENGTH.lower().strip() in ("random", "r"):  # randomly choose a playlist length
            LENGTH = randint(1, TOTAL_SONGS)
        break
    return int(LENGTH)


def checkGuess(GUESS, GENERATION_BASIS):
    """
    determine if program guessed favourite artist/genre correctly
    :param GUESS: str
    :param GENERATION_BASIS: int (use as key for dictionary to convert to a str)
    :return: str
    """
    global BASIS
    RESPONSE = input(f"Is '{GUESS}' your favourite {BASIS[GENERATION_BASIS]}? (y/N) ")
    if RESPONSE.lower().strip() in ("y", "yes"):
        return ">> Hooray! That's a great choice. Thanks for playing and until next time!"
    else:
        return "F"


def getSongID():
    """
    determine ID of song in database
    :return: None
    """
    global CURSOR
    SONGS = CURSOR.execute("""
        SELECT
            id,
            song_name,
            artist
        FROM
            songs
    ;""").fetchall()  # returns a list of tuples

    print("Please select a number:")
    for i in range(len(SONGS)):
        print(f"{i + 1}. '{SONGS[i][1]}' by {SONGS[i][2]}")

    ROW_INDEX = input("> ")
    if not (ROW_INDEX.isnumeric() and int(ROW_INDEX) >= 1 and int(ROW_INDEX) <= len(SONGS)):
        print(">> Please enter a valid number from the list.")
        return getSongID()
    else:
        ROW_INDEX = int(ROW_INDEX) - 1
        return SONGS[ROW_INDEX][0]


def getSongGrouptoRemove(DUPLICATE_DETAILS, DUPLICATE_SONG_IDS):
    """
    display groups of song duplicates then ask user which group to remove
    :param DUPLICATE_DETAILS: list of tuples (names of songs & their artists w/ duplicates) (array parallel to other parameter)
    :param DUPLICATE_SONG_IDS: list of tuples (of groups of song ids that are duplicates of each other)
    :return: tuple (of indices of duplicate song group to clean)
    """
    print("Select a song group to have the duplicates (same song name & artist) removed:")
    for i in range(len(DUPLICATE_DETAILS)):  # number of song groups
        print(f"{i + 1}. '{DUPLICATE_DETAILS[i][0]}' by {DUPLICATE_DETAILS[i][1]} ({len(DUPLICATE_SONG_IDS[i])} potential duplicates found)")

    # determine which group user wants to remove
    GROUP = input("> ")  # correspond to tuple in list, DUPLICATE_SONG_IDS, of song indices user wants cleaned
    if GROUP.isnumeric() and int(GROUP) >= 1 and int(GROUP) <= len(DUPLICATE_DETAILS):
        GROUP = int(GROUP) - 1
        return DUPLICATE_SONG_IDS[GROUP]
    else:
        print(">> Please enter a valid number from the list.")
        return getSongGrouptoRemove(DUPLICATE_DETAILS, DUPLICATE_SONG_IDS)


# --- PROCESSING --- #
def setupSongs(DATA_LIST):
    """
    setup initial songs extracted from CSV file in database
    :param DATA_LIST: list (of tuples)
    :return: None
    """
    global CURSOR, CONNECTION
    CURSOR.execute("""
        CREATE TABLE
            songs (
                id INTEGER PRIMARY KEY,
                song_name TEXT NOT NULL,
                artist TEXT NOT NULL,
                collection_name TEXT NOT NULL,
                duration TEXT NOT NULL,
                genre TEXT NOT NULL
            )
    ;""")
    for i in range(1, len(DATA_LIST)):
        CURSOR.execute("""
            INSERT INTO
                songs
            VALUES (
                ?, ?, ?, ?, ?, ?
            )
        ;""", DATA_LIST[i])
    CONNECTION.commit()


def insertNewSong(SONG_DETAILS):
    """
    add new song to database
    :param SONG_DETAILS: list
    :return: str ("success" alert message)
    """
    global CURSOR, CONNECTION
    NEW_ID = [determineTotalSongs() + 1]
    INFO = NEW_ID + SONG_DETAILS
    CURSOR.execute("""
        INSERT INTO
            songs
        VALUES (
            ?, ?, ?, ?, ?, ?
        )
    ;""", INFO)
    CONNECTION.commit()
    return f"'{SONG_DETAILS[0]}' by {SONG_DETAILS[1]} was successfully added!"


def updateSongDetails(ID, SONG_INFO):
    """
    update song info in database w/ any new info from user
    :param ID: int
    :param SONG_INFO: list
    :return: str ("success" alert message)
    """
    global CURSOR, CONNECTION
    SONG = CURSOR.execute("""
        SELECT 
            *
        FROM
            songs
        WHERE
            id = ?
    ;""", [ID]).fetchone()
    # replace any blank fields (indicates no change to be made) w/ original song details
    for i in range(len(SONG_DETAILS)):
        if SONG_DETAILS[i] == "":
            SONG_DETAILS[i] = SONG[i+1]
    SONG_DETAILS.append(ID)
    # update song details in database
    CURSOR.execute("""
        UPDATE
            songs
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
    return f"'{SONG_DETAILS[0]}' by {SONG_DETAILS[1]} was successfully updated!"


def deleteSong(ID):
    """
    remove song from database
    :param ID: int
    :return: str ('success' message)
    """
    global CURSOR, CONNECTION
    # retrieve song details for ALERT message
    SONG = CURSOR.execute("""
        SELECT
            song_name,
            artist
        FROM
            songs
        WHERE
            id = ?
    ;""", [ID]).fetchone()

    # delete song
    CURSOR.execute("""
        DELETE FROM
            songs
        WHERE
            id = ?
    ;""", [ID])
    CONNECTION.commit()
    return f"'{SONG[0]}' by {SONG[1]} was successfully deleted!"


def generatePlaylist(PLAYLIST_LENGTH):
    """
    generate playlist of specified lengths
    :param PLAYLIST_LENGTH: int
    :return: list (of tuples)
    """
    global randint
    ALL_SONGS = CURSOR.execute("""
        SELECT
            song_name,
            artist,
            genre
        FROM
            songs
    ;""").fetchall()  # returns a list of tuples

    PLAYLIST = []
    SELECTED_INDICES = []
    for i in range(PLAYLIST_LENGTH):
        SONG_INDEX = randint(0, len(ALL_SONGS)-1)
        if SONG_INDEX not in SELECTED_INDICES:
            PLAYLIST.append(ALL_SONGS[SONG_INDEX])
            SELECTED_INDICES.append(SONG_INDEX)
    return PLAYLIST


def determineTotalSongs():
    """
    count total number of songs in database
    :return: int
    """
    global CURSOR
    TOTAL_COUNT = CURSOR.execute("""
        SELECT
            id
        FROM
            songs
    ;""").fetchall()
    return TOTAL_COUNT[-1][0]


def selectArtists() -> list:
    """
    randomly select up to 3 artists to guess as user's favourite artist
    :return: list (of strings)
    """
    global CURSOR, randint
    ALL_ARTISTS = CURSOR.execute("""
        SELECT
            artist
        FROM
            songs
    ;""").fetchall()  # returns 2D array

    UNIQUE_ARTISTS = []
    # save unique names of artists
    for i in range(len(ALL_ARTISTS) - 1, -1, -1):
        if ALL_ARTISTS[i] not in UNIQUE_ARTISTS:
            UNIQUE_ARTISTS.append(ALL_ARTISTS[i])

    # randomly pick artists to guess
    ARTIST_GUESSES = []
    INDEX = randint(0, len(UNIQUE_ARTISTS)-1)
    GUESSED_INDICES = [INDEX]
    ARTIST_GUESSES.append(UNIQUE_ARTISTS[INDEX][0])
    if len(UNIQUE_ARTISTS) >= 2:
        while True:
            INDEX = randint(0, len(UNIQUE_ARTISTS) - 1)
            if INDEX not in GUESSED_INDICES:
                GUESSED_INDICES.append(INDEX)
                ARTIST_GUESSES.append(UNIQUE_ARTISTS[INDEX][0])
                break
    if len(UNIQUE_ARTISTS) >= 3:
        while True:
            INDEX = randint(0, len(UNIQUE_ARTISTS) - 1)
            if INDEX not in GUESSED_INDICES:
                ARTIST_GUESSES.append(UNIQUE_ARTISTS[INDEX][0])
                break
    return ARTIST_GUESSES


def selectGenres() -> list:
    """
    randomly select up to 3 unique genres to guess as user's favourite genre
    :return: list (of strings)
    """
    global CURSOR, randint
    ALL_GENRES = CURSOR.execute("""
            SELECT
                genre
            FROM
                songs
        ;""").fetchall()  # returns 2D array

    UNIQUE_GENRES = []
    # save unique genres
    for i in range(len(ALL_GENRES) - 1, -1, -1):
        if ALL_GENRES[i] not in UNIQUE_GENRES:
            UNIQUE_GENRES.append(ALL_GENRES[i])

    # randomly pick genres to guess
    GENRE_GUESSES = []
    INDEX = randint(0, len(UNIQUE_GENRES) - 1)
    GUESSED_INDICES = [INDEX]
    GENRE_GUESSES.append(UNIQUE_GENRES[INDEX][0])
    if len(UNIQUE_GENRES) >= 2:
        while True:
            INDEX = randint(0, len(UNIQUE_GENRES) - 1)
            if INDEX not in GUESSED_INDICES:
                GUESSED_INDICES.append(INDEX)
                GENRE_GUESSES.append(UNIQUE_GENRES[INDEX][0])
                break
    if len(UNIQUE_GENRES) >= 3:
        while True:
            INDEX = randint(0, len(UNIQUE_GENRES) - 1)
            if INDEX not in GUESSED_INDICES:
                GENRE_GUESSES.append(UNIQUE_GENRES[INDEX][0])
                break
    return GENRE_GUESSES


def getDuplicateSongNames():
    """
    retrieve all names of songs w/ duplicates
    :return: list (of tuples --> names of songs & their artists w/ duplicates in database)
    """
    global CURSOR
    ALL_SONG_NAMES = CURSOR.execute("""
        SELECT
            song_name,
            artist
        FROM
            songs
    ;""").fetchall()

    LISTED_SONGS, LISTED_COUNT = [], []  # parallel arrays
    # save unique names of all songs
    for i in range(len(ALL_SONG_NAMES)-1, -1, -1):
        if ALL_SONG_NAMES[i] not in LISTED_SONGS:
            LISTED_SONGS.append(ALL_SONG_NAMES[i])

    # count number of duplicates of each song
    DUPLICATE_SONGS = []
    for i in range(len(LISTED_SONGS)):
        COUNT = ALL_SONG_NAMES.count(LISTED_SONGS[i])
        if COUNT != 1:
            DUPLICATE_SONGS.append(LISTED_SONGS[i])  # appending tuple of song name + artist
    return DUPLICATE_SONGS


def getDuplicateSongIDs(DUPLICATE_SONGS):
    """
    get all duplicate songs from database (getting their ids specifically)
    :param DUPLICATE_SONGS: list (of tuples consisting of song name & artist w/ duplicates)
    :return: list of tuples (--> song ids of songs that are duplicates of each other)
    """
    global CURSOR
    DUPLICATE_SONG_IDS = []
    for i in range(len(DUPLICATE_SONGS)):
        IDS = CURSOR.execute("""
            SELECT
                id
            FROM
                songs
            WHERE
                song_name = ?
                AND
                artist = ?
        ;""", DUPLICATE_SONGS[i]).fetchall()
        DUPLICATE_GROUP = []
        for j in range(len(IDS)):
            DUPLICATE_GROUP.append(IDS[j][0])
        DUPLICATE_SONG_IDS.append(tuple(DUPLICATE_GROUP))  # 2D array made
    return DUPLICATE_SONG_IDS


def deleteDuplicateSongs(DUPLICATE_SONG_IDS):
    """
    delete all but one of the songs w/ duplicates
    :param DUPLICATE_SONG_IDS: tuple (of indices of songs w/ duplicates (defined as same name & artist))
    :return: str
    """
    global CURSOR, CONNECTION
    # fetch name of song with duplicates being deleted
    SONG = CURSOR.execute("""
        SELECT
            song_name,
            artist
        FROM
            songs
        WHERE
            id = ?
    ;""", [DUPLICATE_SONG_IDS[0]]).fetchone()

    # delete duplicates (leave 1 song in database)
    for i in range(1, len(DUPLICATE_SONG_IDS)):
        CURSOR.execute("""
            DELETE FROM
                songs
            WHERE
                id = ?
        ;""", [DUPLICATE_SONG_IDS[i]])
        CONNECTION.commit()
    return f"Successfully deleted duplicates of '{SONG[0]}' by {SONG[1]}!"


# --- OUTPUTS --- #
def getAllSongsComplete():
    """
    display all song's details except id from database
    :return: None
    """
    global CURSOR
    SONGS = CURSOR.execute("""
        SELECT
            song_name,
            artist,
            collection_name,
            duration,
            genre
        FROM
            songs
    ;""").fetchall()  # returns a list of tuples
    for i in range(len(SONGS)):
        # of the format: 1. song_name by artist on collection_name (duration)
        print(f"{i + 1}. '{SONGS[i][0]}' by {SONGS[i][1]} ", end="")
        #
        if SONGS[i][2] == "Single":
            print(f"({SONGS[i][3]})")  # just duration
        else:
            print(f"on '{SONGS[i][2]}' ({SONGS[i][3]})")  # print album as well
        print(f"Genre: {SONGS[i][-1]} \n")


def displayPlaylist(SONG_DETAILS_PLAYIST):
    """
    display playlist of songs in easy-to-read list
    :param SONG_DETAILS_PLAYIST: list of tuples
    :return: None
    """
    global BASIS
    print("\n>> The playlist generated is:")
    for i in range(len(SONG_DETAILS_PLAYIST)):
        print(f"{i+1}. '{SONG_DETAILS_PLAYIST[i][0]}' by {SONG_DETAILS_PLAYIST[i][1]} (Genre: {SONG_DETAILS_PLAYIST[i][2]})")


# ----- VARIABLES ----- #
DB_NAME = "songs.db"
FIRST_RUN = True
if (Path.cwd() / DB_NAME).exists():
    FIRST_RUN = False

CONNECTION = sqlite3.connect(DB_NAME)
CURSOR = CONNECTION.cursor()

BASIS = {1: "artist", 2: "genre"}

if __name__ == "__main__":
    # -------------------- MAIN PROGRAM CODE -------------------- #
    if FIRST_RUN:
        SONGS = getFileContent("songs.csv")
        setupSongs(SONGS)
    while True:
        print("\n------------------------------------------------------------")
        print("Welcome to your playlist program!")
        # --- inputs
        CHOICE = menu()
        if CHOICE == 2:  # add song
            NEW_SONG = getNewSong()
        elif CHOICE == 3:  # modify song
            SONG_ID = getSongID()
            SONG_DETAILS = getModifiedSongDetails(SONG_ID)
        elif CHOICE == 4:  # remove song
            SONG_ID = getSongID()
        elif CHOICE == 6:  # generate playlist
            PLAYLIST_LENGTH = getPlaylistLength()
        elif CHOICE == 7:  # guess favourites
            GENERATION_BASIS = getGenerationBasis()

        # --- processing
        if CHOICE == 2:  # add song
            ALERT = insertNewSong(NEW_SONG)
        elif CHOICE == 3:  # modify song
            ALERT = updateSongDetails(SONG_ID)
        elif CHOICE == 4:  # remove song
            ALERT = deleteSong(SONG_ID)
        elif CHOICE == 5:  # duplicates
            DUPLICATE_SONG_DETAILS = getDuplicateSongNames()
            DUPLICATE_SONG_GROUPS = getDuplicateSongIDs(DUPLICATE_SONG_DETAILS)
            DUPLICATE_SONG_IDS = getSongGrouptoRemove(DUPLICATE_SONG_DETAILS, DUPLICATE_SONG_GROUPS)
            ALERT = deleteDuplicateSongs(DUPLICATE_SONG_IDS)
        elif CHOICE == 6:  # generate playlist
            PLAYLIST = generatePlaylist(PLAYLIST_LENGTH)
        elif CHOICE == 7:  # guess favourite artist or genre
            if GENERATION_BASIS == 1:  # artist
                ARTISTS = selectArtists()
                for ARTIST in ARTISTS:
                    ALERT = checkGuess(ARTIST, GENERATION_BASIS)
                    if not ALERT == "F":
                        break
                else:
                    ALERT = f">> Darn! Couldn't guess your favourite {BASIS[GENERATION_BASIS]}!"
            else:  # genre
                GENRES = selectGenres()
                for GENRE in GENRES:
                    ALERT = checkGuess(GENRE, GENERATION_BASIS)
                    if not ALERT == "F":
                        break
                else:
                    ALERT = f">> Darn! Couldn't guess your favourite {BASIS[GENERATION_BASIS]}!"

        # --- outputs
        if CHOICE == 1:  # see all songs
            getAllSongsComplete()
        elif CHOICE in (2, 3, 4, 5, 7):  # add, modify, remove, check duplicates, guess favourites
            print(ALERT)
        elif CHOICE == 6:  # generate playlist
            displayPlaylist(PLAYLIST)
        if CHOICE == 8:  # exit
            print("Thanks for using this program!")
            sys.exit()
