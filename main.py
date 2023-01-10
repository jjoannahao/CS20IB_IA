"""
title: Playlist Program
author: Joanna Hao
date-created: 2023-01-01
"""
from pathlib import Path
import sqlite3
from random import randint

"""
reminders:
- IB naming conventions: uppercase for all variables, camelCase for functions/methods
- have the triple line comments for all functions 
"""


# -------------------- SUBROUTINES -------------------- #
# --- INPUTS --- #
def getFileContent(FILENAME):
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
    while True:
        SONG_NAME = input("Name of song? ")
        if SONG_NAME == "":
            print(">> Please enter a song name next time.")
            continue
        ARTIST = input("Name of artist? ")
        if ARTIST == "":
            print(">> Please enter an artist name next time.")
            continue
        COLLECTION = input("Is it part of an album or EP (1), or is it a single? (2) ")
        if not (COLLECTION.isnumeric() and int(COLLECTION) >= 1 and int(COLLECTION) <= 2):
            print(">> Please select a valid number next time.")
            continue
        else:
            if COLLECTION == "1":
                COLLECTION_NAME = input("What is the name of the album or EP? ")
                if COLLECTION_NAME == "":
                    print(">> Please enter an album/EP name next time.")
                    continue
            else:
                COLLECTION_NAME = "Single"
        DURATION = input("Duration of song? ('XX:XX' format) ")
        if not (DURATION.find(":") == 2 and len(DURATION) == 5):
            print(">> Please enter the duration of the song in the format 'XX:XX' next time.")
            continue
        GENRE = input("What is the genre of the song? ")
        if GENRE == "":
            print(">> Please enter a genre next time.")
            continue
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
    global CHOICE
    while True:
        if CHOICE == 6:
            GENERATION_BASIS = input("Do you want the program to generate a playlist by artist (1) or genre (2)? ")
        elif CHOICE == 7:
            GENERATION_BASIS = input("Do you want the program to guess your favourite artist (1) or genre (2)? ")
        if not (GENERATION_BASIS.isnumeric() and int(GENERATION_BASIS) in (1, 2)):
            print("Please select a valid generation basis from the options.")
            continue
        break
    return int(GENERATION_BASIS)


def getPlaylistLength():
    global randint
    TOTAL_SONGS = determineTotalSongs()
    while True:
        LENGTH = input(f"How many songs do you want the playlist to generate? (5-{TOTAL_SONGS} or random (R)) ")
        if not (LENGTH.isnumeric() and int(LENGTH) >= 5 and int(LENGTH) <= TOTAL_SONGS or LENGTH.lower().strip() in (
        "random", "r")):
            print("Please select a valid length or the 'random' option.")
            continue
        elif LENGTH.lower().strip() in ("random", "r"):
            LENGTH = randint(5, TOTAL_SONGS)  # a <= ? <= b for randint (same as randrange(a, b+1)
        break
    return int(LENGTH)


def checkGuess(GUESS, GENERATION_BASIS):
    global BASIS
    RESPONSE = input(f"Is '{GUESS}' your favourite {BASIS[GENERATION_BASIS]}? (y/N) ")
    if RESPONSE.lower().strip() in ("y", "yes"):
        return ">> Hooray! That's a great choice. Thanks for playing and until next time!"
    else:
        return "F"


def getSongID():
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


def getSongGrouptoRemove(DUPLICATE_NAMES, DUPLICATE_SONG_IDS):
    """
    display groups of song duplicates then ask user which group to remove
    :param DUPLICATE_NAMES: list of strings (of songs names w/ duplicates)
    :param DUPLICATE_SONG_IDS: list of tuples (of groups of song ids that are duplicates of each other)
    :return: int (index of song group to remove in DUPLICATE_SONG_GROUPS, the 2D array of duplicate songs
    """
    # display song groups of duplicates
    print(f"len check (shud be =): {len(DUPLICATE_NAMES)}, {len(DUPLICATE_SONG_IDS)}")
    print("Select a song group to have the duplicates (same song name & artist) removed:")
    for i in range(len(DUPLICATE_NAMES)):  # number of song groups
        print("Potential duplicates: ")
        print(f"{i + 1}. {DUPLICATE_NAMES[i]} ", end="")  # format of 1. Song-Name (Num-Duplicates)
        # print(f"({len(DUPLICATE_SONG_IDS[i])})")  # number of duplicates = len of tuple at corresponding index

    # determine which group user wants to remove
    GROUP = input("> ")  # to correspond to index of group in DUPLICATE_SONGS
    if GROUP.isnumeric() and int(GROUP) >= 1 and int(GROUP) <= len(DUPLICATE_NAMES):
        GROUP = int(GROUP) - 1
        return DUPLICATE_SONGS[GROUP]  # list of indexes of duplicates (includes song name still)
    else:
        print("Please enter a valid number from the list.")
        return getSongGrouptoRemove(DUPLICATE_SONGS)


# --- PROCESSING --- #
def setupSongs(DATA_LIST):
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


def getAllSongsBasic():  ### to delete
    global CURSOR
    SONGS = CURSOR.execute("""
        SELECT
            song_name,
            artist
        FROM
            songs
    ;""").fetchall()  # returns a list of tuples

    for i in range(len(SONGS)):
        print(f"{i + 1}. '{SONGS[i][0]}' by {SONGS[i][1]}")  # of the format: 1. (song_name) by (artist)


def insertNewSong(SONG_DETAILS):
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



def updateSongDetails(ID):
    global CURSOR, CONNECTION
    SONG = CURSOR.execute("""
        SELECT 
            *
        FROM
            songs
        WHERE
            id = ?
    ;""", [ID]).fetchone()
    SONG_DETAILS = getModifiedSongDetails(ID)
    for i in range(len(SONG_DETAILS)):
        if SONG_DETAILS[i] == "":
            SONG_DETAILS[i] = SONG[i+1]
    SONG_DETAILS.append(ID)
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
            songs
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
    else:  # if no ties
        TOP = [TOP_COUNT]
    return TOP


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
            songs
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
    else:  # if no ties
        TOP = [TOP_COUNT]
    return TOP

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
    ### Need to account for duplicate songs beforehand
    PLAYLIST = []
    SELECTED_INDICES = []
    for i in range(PLAYLIST_LENGTH):
        SONG_INDEX = randint(0, len(ALL_SONGS)-1)
        if SONG_INDEX not in SELECTED_INDICES:
            PLAYLIST.append(ALL_SONGS[SONG_INDEX])
            SELECTED_INDICES.append(SONG_INDEX)
    return PLAYLIST


def determineTotalSongs():
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


def findArtistByCount(ARTISTS_COUNT, ALL_ARTISTS):
    ARTIST_COUNT = max(ARTISTS_COUNT)  # find top artist by count
    ARTIST_INDEX = ARTISTS_COUNT.index(ARTIST_COUNT)  # obtain index to get artist name
    ARTIST = ALL_ARTISTS[ARTIST_INDEX]  # get artist name
    ARTISTS_COUNT.pop(ARTIST_INDEX)  # remove so next top artist can be found
    return ARTIST


def findGenrebyCount(GENRES_COUNT, ALL_GENRES):
    GENRE_COUNT = max(GENRES_COUNT)
    GENRE_INDEX = GENRES_COUNT.index(GENRE_COUNT)
    GENRE = ALL_GENRES[GENRE_INDEX]
    GENRE_COUNT.pop(GENRE_INDEX)
    return GENRE


def getDuplicateSongNames():
    """
    retrieve all names of songs w/ duplicates
    :return: list (of strings --> names of songs w/ duplicates)
    """
    global CURSOR
    ALL_SONG_NAMES = CURSOR.execute("""
        SELECT
            song_name
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
            DUPLICATE_SONGS.append(LISTED_SONGS[i][0])
    #
    #     LISTED_COUNT.append(COUNT)
    # # assemble names of songs w/ duplicates
    # DUPLICATE_SONGS = []
    # for INDEX, VALUE in enumerate(LISTED_COUNT):
    #     if VALUE != 1:  # duplicates found
    #         DUPLICATE_SONGS.append(LISTED_SONGS[INDEX])
    return DUPLICATE_SONGS


def getDuplicateSongIDs(DUPLICATE_SONGS):
    """
    get all duplicate songs from database (getting their ids specifically)
    :param DUPLICATE_SONGS: list (of song names that have duplicates present)
    :return: list of tuples (--> song ids of songs that are duplicates of each other)
    """
    global CURSOR
    DUPLICATE_SONG_IDS = []
    for INDEX, SONG_NAME in enumerate(DUPLICATE_SONGS):
        IDS = CURSOR.execute("""
            SELECT
                id
            FROM
                songs
            WHERE
                song_name = ?
        ;""", [SONG_NAME]).fetchall()
        DUPLICATE_GROUP = []
        for i in range(len(IDS)):
            DUPLICATE_GROUP.append(IDS[i][0])
        DUPLICATE_SONG_IDS.append(tuple(DUPLICATE_GROUP))  # 2D array made
    return DUPLICATE_SONG_IDS


def deleteDuplicateSongs(DUPLICATE_SONGS):
    """
    delete all but one of the songs w/ duplicates
    :param DUPLICATE_SONGS: list (of song_name then IDs of all songs sharing that name & artist)
    :return: str
    """
    global CURSOR, CONNECTION
    for i in range(2, len(DUPLICATE_SONGS)):  # leave one song in the database
        CURSOR.execute("""
            DELETE FROM
                songs
            WHERE 
                id = ?
        ;""", [DUPLICATE_SONGS[i]])
    return f"Successfully deleted duplicates of {DUPLICATE_SONGS[0]}"


# --- OUTPUTS --- #
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
            DUPLICATE_SONG_NAMES = getDuplicateSongNames()
            DUPLICATE_SONG_GROUPS = getDuplicateSongIDs(DUPLICATE_SONG_NAMES)
            DUPLICATE_SONG_IDS = getSongGrouptoRemove(DUPLICATE_SONG_NAMES, DUPLICATE_SONG_GROUPS)  # debugging currently (not sure if 2 params are parallel arrays)
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
        elif CHOICE in (2, 3, 4, 5, 7):
            print(ALERT)
        elif CHOICE == 6:  # generate playlist
            displayPlaylist(PLAYLIST)
        if CHOICE == 8:
            print("Thanks for using this program!")
            exit()
