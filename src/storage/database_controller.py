from tinydb import TinyDB
from src.services.api_service import APIService
from os import getcwd, remove, path
from json import dump, load


def save_library():
    filename = path.dirname(getcwd()) + rf'\sync_info\library.db'
    delete_library()
    library = TinyDB(filename)
    api_serv = APIService()
    full_lib = api_serv.get_user_library_info(storing=True)
    fav_index = 0
    for i, item in enumerate(full_lib):
        if item['id'] == 'fav':
            fav_index = i
            break
    for i, lib_item in enumerate(full_lib):
        if i > fav_index:
            songs = api_serv.get_album_songs_info(lib_item['id'], lib_item['size'], storing=True)
        elif i == fav_index:
            songs = api_serv.get_favourite_songs_info(storing=True)
        else:
            songs = api_serv.get_playlist_songs_info(lib_item['id'], lib_item['size'], storing=True)
        library.insert({'name': lib_item['name'], 'size': lib_item['size'], 'songs': songs})
    content = library.all()
    with open(filename, 'w') as file:
        dump(content, file)


def load_library():
    filename = path.dirname(getcwd()) + rf'\sync_info\library.db'
    try:
        with open(filename, 'r') as file:
            return load(file)
    except FileNotFoundError:
        return


def delete_library():
    filename = path.dirname(getcwd()) + rf'\sync_info\library.db'
    try:
        if path.isfile(filename):
            remove(filename)
    except FileNotFoundError or PermissionError:
        pass


def check_if_library_exists():
    filename = path.dirname(getcwd()) + rf'\sync_info\library.db'
    try:
        return path.isfile(filename)
    except FileNotFoundError:
        return False
