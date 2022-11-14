import sqlite3


def sql_select(obj, table, condition=''):
    if condition != '':
        condition = 'WHERE ' + condition
    else:
        condition = ''

    con = sqlite3.connect('Settings/tracks.db')
    res = con.execute(f"""SELECT {obj} FROM {table} {condition}""").fetchall()
    con.close()

    return res


async def sql_insert(table, value):
    print(value)
    try:
        con = sqlite3.connect('Settings/tracks.db')
        cur = con.cursor()
        cur.execute(
            f"""INSERT INTO {table}(id, name, author, download, iconsD, duration_ms) VALUES {value}""")
        con.commit()
        con.close()

    except sqlite3.Error as err:
        print(err)


def load_json(file):
    with open(f'Settings/{file}') as json_file:
        res = eval(json_file.readline())
    return res


def save_json(file, json):
    with open(f'Settings/{file}', 'w') as f:
        print(json, file=f)


def icon_status(track_id=None):
    con = sqlite3.connect('Settings/tracks.db')
    res = list(map(lambda x: int(x[0]), con.execute("""SELECT id FROM track WHERE iconsD = 1""").fetchall()))
    con.close()
    return res


def playlist_name(playlist_id):
    con = sqlite3.connect('Settings/tracks.db')
    res = list(map(lambda x: x[0], con.execute(f"""SELECT name FROM names 
    WHERE playlistID == {playlist_id}""").fetchall()))
    con.close()
    return res[0]


def all_playlist():
    con = sqlite3.connect('Settings/tracks.db')
    res = list(map(lambda x: x[0], con.execute("""SELECT playlistID FROM names""").fetchall()))
    con.close()
    return res
