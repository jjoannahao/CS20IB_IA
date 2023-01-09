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
    while True:
        GENERATION_BASIS = input("Do you want to generate a playlist by artist (1) or genre (2)? ")
        if not (GENERATION_BASIS.isnumeric() and int(GENERATION_BASIS) in (1, 2)):
            print("Please select a valid generation basis from the options.")
            continue
        break
    return int(GENERATION_BASIS)


def getPlaylistLength():
    global TOTAL_SONGS, randint
    while True:
        LENGTH = input(f"How many songs do you want the playlist to generate? (5-{TOTAL_SONGS} or random (R)) ")
        if not (LENGTH.isnumeric() and int(LENGTH) >= 5 and int(LENGTH) <= TOTAL_SONGS or LENGTH.lower().strip() in (
        "random", "r")):
            print("Please select a valid length or the random option.")
            continue
        elif LENGTH.lower().strip() in ("random", "r"):
            LENGTH = randint(5, TOTAL_SONGS)  # a <= ? <= b for randint (same as randrange(a, b+1)
        break
    return LENGTH


def checkGuess(GUESS, GENERATION_BASIS):
    global BASIS
    RESPONSE = input(f"Is {GUESS} your favourite {BASIS[GENERATION_BASIS]}? (y/N) ")
    if RESPONSE.lower().strip() in ("y", "yes"):
        ALERT = "Hooray! That's a great choice. Thanks for playing and until next time!"
        return ALERT
    else:
        return False


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


def getSongGrouptoRemove(DUPLICATE_SONGS):
    """
    display groups of song duplicates then ask user which group to remove
    :param DUPLICATE_SONGS: list of lists (song_name, ids of duplicate songs in database)
    :return: list (of indexes of song duplicates)
    """
    # display song groups of duplicates
    print("Select a song group to have the duplicates (same song name & artist) removed:")
    for i in range(len(DUPLICATE_SONGS)):  # number of song groups
        DUPLICATES_NUMBER = len(DUPLICATE_SONGS[i] - 1)  # minus song name
        print(f"{i + 1}. {DUPLICATE_SONGS[i][0]} ({DUPLICATES_NUMBER})")  # format of 1. Song-Name (Num-Duplicates)

    # determine which group user wants to remove
    GROUP = input("> ")  # to correspond to index of group in DUPLICATE_SONGS
    if GROUP.isnumeric() and int(GROUP) >= 1 and int(GROUP) <= len(DUPLICATE_SONGS):
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


def generateArtistPlaylist(TOP_COUNT, TOP, PLAYLIST_LENGTH):
    global TOTAL_SONGS, randint
    PLAYLIST = []
    # determining number of songs from top artists
    TOP_PORTION = int(TOP_COUNT / TOTAL_SONGS)  # floored (rounded down)
    SONGS_PER_BASIS = [(PLAYLIST_LENGTH * TOP_PORTION) for i in range(len(TOP))]  # SONGS_PER_BASIS parallel to TOP
    # add songs from top artist(s)
    for i in range(len(SONGS_PER_BASIS)):
        for j in range(SONGS_PER_BASIS[i]):
            SONG_INDEX = randint(0, TOP_COUNT-1)
            PLAYLIST.append(SONG_INDEX)
    # add songs not from top artists
    for i in range(PLAYLIST_LENGTH - int(len(PLAYLIST))):
        SONG_INDEX = randint(0, TOTAL_SONGS-1)
        while True:
            if SONG_INDEX in TOP:  ### CHECK TYPES so in statement actually works
                SONG_INDEX = randint(0, TOTAL_SONGS)
            else:
                break
    return PLAYLIST


def generateGenrePlaylist(TOP_COUNT, TOP, PLAYLIST_LENGTH):
    global TOTAL_SONGS, randint
    PLAYLIST = []
    TOP_PORTION = int(TOP_COUNT / TOTAL_SONGS)
    # add songs from top genre to playlist
    for i in range(TOP_PORTION):
        SONG_INDEX = randint(0, TOP_COUNT-1)  ### CHECK
        PLAYLIST.append(TOP[SONG_INDEX])
    # add songs not from top genre
    for i in range(PLAYLIST_LENGTH - int(len(PLAYLIST))):
        SONG_INDEX = randint(0, TOTAL_SONGS-1)
        while True:  # ensure songs not from top genre selected
            if SONG_INDEX in TOP:  ### CHECK TYPES so in statement actually works
                SONG_INDEX = randint(0, TOTAL_SONGS)
            else:
                break
    return PLAYLIST


def retrievePlaylistSongs(INDICES_PLAYLIST):
    """
    using generated indices, select songs from database
    :param INDICES_PLAYLIST: list (of indices of songs generated)
    :return: list
    """
    global CURSOR, CONNECTION
    SONG_DETAILS_PLAYLIST = []
    for i in range(len(INDICES_PLAYLIST)):
        RETRIEVED_SONG = CURSOR.execute("""
            SELECT
                song_name,
                artist
            FROM
                songs
            WHERE
                id = ?
        ;""", [INDICES_PLAYLIST[i]])
        SONG_DETAILS_PLAYLIST.append(RETRIEVED_SONG)
    return SONG_DETAILS_PLAYLIST


def determineTotalSongs():
    global CURSOR
    TOTAL_COUNT = CURSOR.execute("""
        SELECT
            song_name
        FROM
            songs
    ;""").fetchall()
    return len(TOTAL_COUNT)


def determineTop3Artists():
    global CURSOR
    ALL_ARTISTS = CURSOR.execute("""
        SELECT
            artist
        FROM
            songs
    ;""").fetchall()  # returns 2D array

    LISTED_ARTISTS, ARTISTS_COUNT = [], []  # parallel arrays
    # save unique names of artists
    for i in range(len(ALL_ARTISTS)-1, -1, -1):
        if ALL_ARTISTS[i] not in LISTED_ARTISTS:
            LISTED_ARTISTS.append(ALL_ARTISTS[i])
    #     else:
    #         ALL_ARTISTS.pop(i)
    #
    # # count number of songs per artist
    # for ARTIST in ALL_ARTISTS:
    #     COUNT = CURSOR.execute("""
    #         SELECT
    #             COUNT(artist)
    #         FROM
    #             songs
    #         WHERE
    #             artist = ?
    #     ;""", [ARTIST])
    #     ARTISTS_COUNT.append(COUNT)  # parallel array
    for i in range(len(LISTED_ARTISTS)):
        COUNT = ALL_ARTISTS.count(LISTED_ARTISTS[i])
        ARTISTS_COUNT.append(COUNT)

    print(LISTED_ARTISTS)  # 2D Array still

    ARTIST1 = sortBasisForTop(ARTISTS_COUNT)
    ARTIST1 = LISTED_ARTISTS[sortBasisForTop(ARTISTS_COUNT)][0]

    TOP_ARTISTS = [ARTIST1]

    if UNIQUE_ARTIST_COUNT >= 2:
        ARTIST2 = LISTED_ARTISTS[sortBasisForTop(ARTISTS_COUNT)][0]

        ARTISTS_COUNT.pop(ARTIST2[1])
        LISTED_ARTISTS.pop(ARTIST2[1])
        TOP_ARTISTS.append(ARTIST2)
    elif UNIQUE_ARTIST_COUNT >= 3:
        ARTIST3 = LISTED_ARTISTS[sortBasisForTop(ARTISTS_COUNT)][0]
        TOP_ARTISTS.append(ARTIST3)
    return TOP_ARTISTS


    # ARTIST1 = findArtistByCount(ARTISTS_COUNT, ALL_ARTISTS)
    # TOP_ARTISTS = [ARTIST1]
    # if len(ARTISTS_COUNT) >= 2:
    #     ARTIST2 = findArtistByCount(ARTISTS_COUNT, ALL_ARTISTS)
    #     TOP_ARTISTS.append(ARTIST2)
    # elif len(ARTISTS_COUNT) >= 3:
    #     ARTIST3 = findArtistByCount(ARTISTS_COUNT, ALL_ARTISTS)
    #     TOP_ARTISTS.append(ARTIST3)
    # return TOP_ARTISTS
    ## original
    # ARTIST1_COUNT = max(ARTISTS_COUNT)  # find top artist by count
    # ARTIST1_INDEX = ARTISTS_COUNT.index(ARTIST1_COUNT)  # obtain index to get artist name
    # ARTIST1 = ALL_ARTISTS[ARTIST1_INDEX]  # get artist name
    # ARTISTS_COUNT.remove(ARTIST1_COUNT)  # remove so next top artist can be found


def sortBasisForTop(BASIS_COUNT):
    TOP_COUNT = [0, 0]  # top_value, index
    for INDEX, VALUE in enumerate(BASIS_COUNT):
        if VALUE > TOP_COUNT[0]:
            TOP_COUNT[0] = VALUE
            TOP_COUNT[1] = INDEX
    return TOP_COUNT[1]


def determineTop3Genres():
    global CURSOR
    ALL_GENRES = CURSOR.execute("""
        SELECT
            genre
        FROM
            songs
    ;""").fetchall()
    LISTED_GENRES, GENRES_COUNT = [], []

    # remove duplicates
    for i in range(len(ALL_GENRES) - 1, -1, -1):
        if ALL_GENRES[i] not in LISTED_GENRES:
            LISTED_GENRES.append(ALL_GENRES[i])
        else:
            ALL_GENRES.pop(i)

    # count number of songs per genre
    for GENRE in ALL_GENRES:
        COUNT = CURSOR.execute("""
            SELECT
                COUNT(genre)
            FROM
                songs
            WHERE
                artist = ?
        ;""", [GENRE])
    GENRES_COUNT.append(COUNT)  # parallel array

    GENRE1 = findGenrebyCount(GENRES_COUNT, ALL_GENRES)
    TOP_GENRES = [GENRE1]
    if len(GENRES_COUNT) >= 2:
        GENRE2 = findArtistByCount(GENRES_COUNT, ALL_GENRES)
        TOP_GENRES.append(GENRE2)
    elif len(GENRES_COUNT) >= 3:
        GENRE3 = findArtistByCount(GENRES_COUNT, ALL_GENRES)
        TOP_GENRES.append(GENRE3)
    return TOP_GENRES


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
    :return:
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
    for i in range(len(LISTED_SONGS)):
        COUNT = ALL_SONG_NAMES.count(LISTED_SONGS[i])
        LISTED_COUNT.append(COUNT)
    # assemble names of songs w/ duplicates
    DUPLICATE_SONGS = []
    for INDEX, VALUE in enumerate(LISTED_COUNT):
        if VALUE != 1:  # duplicates found
            DUPLICATE_SONGS.append(LISTED_SONGS[INDEX])
    return DUPLICATE_SONGS


def getAllDuplicateSongs(DUPLICATE_SONGS):
    """
    get all duplicate songs from database (getting their ids specifically)
    :param DUPLICATE_SONGS: list of song names (duplicates present)
    :return:
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
        IDS.insert(0, SONG_NAME)  # insert song_name at start
        DUPLICATE_SONG_IDS.append(IDS)  # 2D array made
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
def displayPlaylist(SONG_DETAILS_PLAYIST, GENERATION_BASIS):
    """
    display playlist of songs in easy-to-read list
    :param SONG_DETAILS_PLAYIST: list of tuples
    :param GENERATION_BASIS: int (1 = artist, 2 = genre)
    :return: None
    """
    global BASIS
    print(f"The playlist generated based on your favourite {BASIS[GENERATION_BASIS]} is:")
    for i in range(len(SONG_DETAILS_PLAYIST)):
        print(f'{i+1}. "{SONG_DETAILS_PLAYIST[0]}" by {SONG_DETAILS_PLAYIST[1]}')


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
            GENERATION_BASIS = getGenerationBasis()
            PLAYLIST_LENGTH = getPlaylistLength()
        elif CHOICE == 7:  # guess favourites
            GENERATION_BASIS = getGenerationBasis()

        # --- processing
        TOTAL_SONGS = determineTotalSongs()  # starts counting from 1 (?)
        if CHOICE == 2:  # add song
            ALERT = insertNewSong(NEW_SONG)
        elif CHOICE == 3:  # modify song
            ALERT = updateSongDetails(SONG_ID)
        elif CHOICE == 4:  # remove song
            ALERT = deleteSong(SONG_ID)
        elif CHOICE == 5:  # duplicates
            DUPLICATE_SONG_NAMES = getDuplicateSongNames()
            DUPLICATE_SONG_GROUPS = getAllDuplicateSongs(DUPLICATE_SONG_NAMES)
            DUPLICATE_SONG_IDS = getSongGrouptoRemove(DUPLICATE_SONG_GROUPS)
            ALERT = deleteDuplicateSongs(DUPLICATE_SONG_IDS)
        elif CHOICE == 6:  # generate playlist
            if GENERATION_BASIS == 1:  # artist
                INDICES_OF_TOP = determineTopArtist()
                INDICES_PLAYLIST = generateArtistPlaylist(len(INDICES_OF_TOP), INDICES_OF_TOP, PLAYLIST_LENGTH)
                SONGS_PLAYLIST = retrievePlaylistSongs(INDICES_PLAYLIST)
            else:  # genre
                INDICES_OF_TOP = determineTopGenre()
                INDICES_PLAYLIST = generateGenrePlaylist(len(INDICES_OF_TOP), INDICES_OF_TOP, PLAYLIST_LENGTH)
                SONGS_PLAYLIST = retrievePlaylistSongs(INDICES_PLAYLIST)
        elif CHOICE == 7:  # guess favourite ____
            if GENERATION_BASIS == 1:  # artist
                TOP_ARTISTS = determineTop3Artists()
                print(TOP_ARTISTS)
                # for ARTIST in TOP_ARTISTS:
                #     ALERT = checkGuess(ARTIST, GENERATION_BASIS)
                #     if not ALERT:
                #         break
                # else:
                #     ALERT = "Darn! Couldn't guess it!"
            else:  # genre
                TOP_GENRES = determineTop3Genres()
                for GENRE in TOP_GENRES:
                    ALERT = checkGuess(GENRE, GENERATION_BASIS)
                    if not ALERT:
                        break
                else:
                    ALERT = "Darn! Couldn't guess it!"

        # --- outputs
        if CHOICE == 1:  # see all songs
            getAllSongsComplete()
        # elif CHOICE in (2, 3, 4, 5, 7):
        #     print(ALERT)
        # elif CHOICE == 6:  # generate playlist
        #     displayPlaylist(SONGS_PLAYLIST, GENERATION_BASIS)
        if CHOICE == 8:
            print("Thanks for using this program!")
            exit()
