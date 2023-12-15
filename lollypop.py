import os
import sys
import hashlib
import sqlite3
import argparse
from datetime import datetime

def main():
    # start-up
    print("Lollypop starting")
    args = get_args()
    database = args[0]
    target = args[1]

    # check database path is valid
    ## confirm the path given is a file or directory we can find and return the absolute path
    database_info = test_path(database, "return")

    ## attempt to access and backup the database on the supplied path
    match database_info["path_type"]:
        case "file": #check the database is ours
            suggestion = database_info["path"]
            question(f"Please confirm {suggestion} is the path to database?")
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
            push_db(suggestion,"CREATE TABLE [pool0] (md5sum TEXT, filepath TEXT, parent TEXT, filename TEXT, size TEXT, mdate TEXT)")
            push_db(suggestion,"INSERT INTO log VALUES ('name', :name)",{"name": name})
            push_db(suggestion,"INSERT INTO log VALUES ('edited', :time)",{"time": timestamp()})
        case "directory":
            print(f"Expected file not directory: {database_info['path']}")
            abort(1)
        case _:
            print(f"Unknown path type: {database_info['path']}")
            abort(1)
    
    # check the path for the read directory is correct
    target_info = test_path(target, "directory")
    match target_info["path_type"]:
        case "file":
            print(f"Expected directory not file: {target_info['path']}")
            abort(1)
        case "not_found":
            print(f"Target directory not found: {target_info['path']}")
            abort(1)
        case "directory":
            target = target_info['path']
            question(f"Please confirm target directory: {target}")
            print(f"Walking {target}")
            walk_path(target, suggestion)
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
    parser.add_argument("target", type=str, nargs=1, help="Path to the directory you want to add to the dedupe database.")
    args = parser.parse_args()
    database = args.database.pop(0)
    target = args.target.pop(0)
    if database == "":
        print("Invalid path to database: \"\"")
        abort(1)
    elif target == "":
        print("Invalid path to target: \"\"")
        abort(1)
    
    return [ database, target ]

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
    #print(f"query: {query}")
    #print(f"params: {params}")
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
        #print(f"changes: {connection.total_changes}")
        if connection is not None:
            connection.close()

def pull_db(db, query, params=False):
    #print(f"query: {query}")
    #print(f"params: {params}")
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
        #print(f"changes: {connection.total_changes}")
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
    return timestamp

def walk_path(path, db):
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
            size = get_size(filepath)
            mdate = get_modifidation_date(filepath)
            md5sum = get_md5sum(filepath)
            data = {
                "md5sum": md5sum,
                "filepath": filepath,
                "parent": parent,
                "filename": file,
                "size": size,
                "mdate": mdate
            }
            push_db(db,"INSERT INTO pool0 VALUES (:md5sum, :filepath, :parent, :filename, :size, :mdate)", data)

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

def get_size(path):
    try:
        size = os.path.getsize(path)
    except:
        size = "0kB"
    else:
        # os.path.getsize returns in bytes
        # 1000 bytes in a kilobyte (kB)
        # 1000000 bytes in a megabyte (MB)
        # 1000000000 bytes in a gigabyte (GB)
        # TODO: test for where to put the decimal in order to convert sizes
        if size <= 999:
            size = str(size)
            size = f"{size}B"
        elif size <= 999999:
            size = size/1000
            size = round(size, 2)
            size = str(size)
            size = f"{size}MB"
        elif size >= 1000000:
            size = size/1000000
            size = round(size, 2)
            size = str(size)
            size = f"{size}GB"
        else:
            print(f"Unknown file size: {size}")
            abort(1)    
    finally:
        return size

def get_modifidation_date(path):
    try:
        mtime = os.path.getmtime(path)
    except:
        mtime = 0
    
    try:
        mtime = datetime.fromtimestamp(mtime)
        mtime = str(mtime)
    except:
        print(f"Unknown date: {mtime}")
        abort(1)
    finally:
        return mtime
    

if __name__ == "__main__":
    main()