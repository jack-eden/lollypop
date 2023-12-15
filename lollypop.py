import os
import sys
import shutil
import hashlib
import sqlite3
import argparse
from datetime import datetime

def main():
    # start-up
    print("Lollypop starting")
    args = get_args()
    database = args[0]

    # check database path is valid
    ## confirm the path given is a file or directory we can find and return the absolute path
    database_info = test_path(database, "return")

    ## attempt to access and backup the database on the supplied path
    match database_info["path_type"]:
        case "file": #check the database is ours
            suggestion = database_info["path"]
            question("Please confirm this is the path to database?")
            print(f"Trying database: {database_info['path']}")
            rows = pull_db(suggestion,"SELECT key, value FROM log")
            print(rows)
            # TODO backup db here
        case "not_found": #create a new database
            suggestion = database_info["path"]
            parent = path_segments(suggestion, "parent")
            name = path_segments(suggestion, "file")
            parent_info = test_path(parent, "directory")
            question("Please confirm you are happy to create a NEW database at this location?")
            print(f"Creating new database at {suggestion}")
            push_db(suggestion,"CREATE TABLE [log] (key TEXT, value TEXT)")
            push_db(suggestion,"INSERT INTO log VALUES ('name', :name)",{"name": name})
            push_db(suggestion,"INSERT INTO log VALUES ('edited', :time)",{"time": timestamp()})
        case "directory":
            print(f"Expected file not directory: {database_info['path']}")
            abort(1)
        case _:
            print(f"Unknown path type: {database_info['path']}")
            abort(1)
    
    print("Done.")

def get_args():
    parser = argparse.ArgumentParser(
        prog="Lollypop",
        description="Helper script written to dedup files across multiple hardrives",
        epilog="")
    parser.add_argument("database", type=str, nargs=1, help="Path to sqlite database file.")
    args = parser.parse_args()
    database = args.database.pop(0)
    if database == "":
        print("Invalid path: \"\"")
        sys.exit(1)
    
    return [ database ]

def test_path(path, test):
    try:
        absolutepath = os.path.abspath(path)
    except Exception as error:
        print(f"{print_err(1)}: {path}")
        print(f"{error}")
        sys.exit(1)
    
    isfile = os.path.isfile(absolutepath)
    isdir = os.path.isdir(absolutepath)

    match test:
        case "return":
            if isfile == True:
                result = "file"
            elif isdir == True:
                result = "directory"
            else:
                print(f"Unknown path: {absolutepath}")
                result = "not_found"
        case "file":
            if isfile == True and test == "file":
                result = "file"
            elif isfile == False and test == "file":
                print(f"Expected file not found, {absolutepath} is a directory.")
                sys.exit(1)
        case "directory":
            if isdir == True and test == "directory":
                result = "directory"
            elif isdir == False and test == "directory":
                print(f"Expected directory not found, {absolutepath} is a file.")
                sys.exit(1)
        case _:
            print(f"No test condition supplied for given path: {absolutepath}")
            sys.exit(1)
    
    return { "path": absolutepath, "path_type": result }

def path_segments(path, requested_segment):
    segments = path.split("/")
    file = segments[-1]
    del segments[-1]
    parent = "/".join(segments)

    match requested_segment:
        case "file":
            return file
        case "parent":
            return parent
        case _:
            print(f"Unknown path segment request: {requested_segment}")
            sys.exit(1)

def question(text):
    while True:
        print(text)
        print("[Y]es, [N]o, [Q]uit")
        dialog = input()

        match dialog:
            case "y" | "Y":
                break
            case "n" | "N":
                abort(0)
            case "q" | "Q":
                abort(0)
            case _:
                print("Unrecognised input")
                continue

def abort(status):
    print("Aborting")
    sys.exit(status)

def push_db(db, query, params=False):
    print(f"query: {query}")
    print(f"params: {params}")
    try:
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
    except Error as message:
        print(message)
        condition.close()
        abort(1)
    else:
        if params == False:
            cursor.execute(query)
        else:
            params = (params)
            cursor.execute(query,params)
    finally:
        connection.commit()
        print(f"changes: {connection.total_changes}")
        if connection is not None:
            connection.close()

def pull_db(db, query, params=False):
    print(f"query: {query}")
    print(f"params: {params}")
    try:
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
    except Error as message:
        print(message)
        condition.close()
        abort(1)
    else:
        if params == False:
            rows = cursor.execute(query).fetchall()
        else:
            params = (params)
            rows = cursor.execute(query,params).fetchall()
    finally:
        connection.commit()
        print(f"changes: {connection.total_changes}")
        if connection is not None:
            connection.close()
        return rows

def timestamp_db(db):
    try:
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
    except Error as message:
        print(message)
        condition.close()
        abort(1)
    else:
        data = (
            {"time": timestamp()}
        )
        cursor.execute("""UPDATE log SET value = :time WHERE key = 'edited'""", data)
    finally:
        connection.commit()
        if connection is not None:
            connection.close()

def timestamp():
    timestamp = datetime.now()
    timestamp = str(timestamp)
    timestamp = timestamp.replace("-", "")
    timestamp = timestamp.replace(" ", "")
    timestamp = timestamp.replace(":", "")
    timestamp = timestamp.replace(".", "")
    return timestamp

def walk_path(path):
    for (root,dirs,files) in os.walk(path, topdown=True):
        for folder in dirs:
            if folder[0] == ".":
                dirs.remove(folder)
        for file in files:
            if file[0] == ".":
                files.remove(file)
        for file in files:
            filepath = "/".join([root,file])
            parent = root
            parent = parent.split("/")
            parent = parent[-1]
            md5sum = get_md5sum(filepath)
            print(f"{md5sum}, {filepath}, {parent}/{file}")

def get_md5sum(filepath):
    BUF_SIZE = 65536  # 64kb
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    md5sum = md5.hexdigest()
    return md5sum

if __name__ == "__main__":
    main()