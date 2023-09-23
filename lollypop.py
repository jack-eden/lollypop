import os
import sys
import hashlib
import sqlite3
import argparse

def main():
    print("Lollypop starting...")

    args = startup()
    RUNNINGDIR = args[0]
    STARTDB = args[1]

    path_chunks = check_path(STARTDB) # [ exists, dbname, dbpath ] OR [ "error", error string, dbpath]
    if path_chunks[0] == "error":
        print(errstring[path_chunks[1]])
        print("'",path_chunks[2],"'")
        path_chunks = input_db_path()
    path_chunks = input_confirm_db(path_chunks)
    DBEXISTS = path_chunks[0]
    DBNAME = path_chunks[1]
    DBPATH = path_chunks[2]

    if DBEXISTS == True:
        check_db([DBNAME, DBPATH]) # TODO
    else:
        create_db([DBNAME, DBPATH]) # TODO
    
    #print(f"starting from: {SPATH}")
    #print(f"using database: {dblocation}")

    #walk_path(SPATH)
    aborting()



def startup():
    runningdir = os.getcwd() # get the directory we're running in
    runningdir = get_absolutepath(runningdir)
    parser = argparse.ArgumentParser(
                    prog="Lollypop",
                    description="""
                    Helper script written to dedup 
                    files across multiple hardrives""",
                    epilog="")
    parser.add_argument("database", type=str, nargs="+",
                    help="path to sqlite database file")
    args = parser.parse_args()
    database = args.database.pop(0)
    database = get_absolutepath(database)
    return [ runningdir, database ]



def check_path(path):
    dbpath = get_absolutepath(path)
    dbpath_isfile = os.path.isfile(dbpath)
    dbpath_isdir = os.path.isdir(dbpath) 
    segments = path.split("/")

    if dbpath_isfile == True:
        dbname = segments[-1]
        filetype = check_filetype(dbname)
        if filetype == False:
            return [ "error", "invalid filetype", dbpath]
        exists = True
        return [ exists, dbname, dbpath ]
    elif dbpath_isdir == True:
        dbname = "lollypop.db"
        dbpath = "/".join(dbpath,dbname)
        exists = False
        return [ exists, dbname, dbpath ]
    else:
        dbname = segments[-1]
        del segments[-1]
        dbdir = "/".join(segments)
        dbpath_isdir = os.path.isdir(dbdir) 
        if dbpath_isdir == False:
            return [ "error", "unknown dir", dbpath]
        filetype = check_filetype(dbname)
        if filetype == False:
            return [ "error", "invalid filetype", dbpath]
        exists = False
        return [ exists, dbname, dbpath ]



def input_confirm_db(list): # [ exists, dbname, dbpath ]
    exists = list[0]
    dbname = list[1]
    dbpath = list[2]

    while True:
        print(f"database name: {dbpath}")
        print("continue with current database?:")
        print("")
        print("y: continue with these settings")
        print("n: change database")
        print("q: exit and quit")
        dialog = input("")

        match dialog:
            case "y" | "Y":
                break
            case "n" | "N":
                newpath = input_db_path()
                input_confirm_db(newpath)
            case "q" | "Q":
                aborting()
            case _:
                print(errstring["input"])
                continue
    
    exists = exists
    dbname = dbname
    dbpath = dbpath
    return [ exists, dbname, dbpath ]



def input_db_path():
    # TODO add prefill suggestion that uses current dbpath or startdir
    while True:
        print("Please enter path to database or 'q' to quit:")
        dialog = input("")

        match dialog:
            case "q" | "Q":
                aborting()
            case _:
                path_chunks = check_path(dialog) # [ exists, dbname, dbpath ] OR [ "error", error string, dbpath]
                if path_chunks[0] == "error":
                    print(errstring[path_chunks[1]])
                    print("'",path_chunks[2],"'")
                    input_db_path()
                return path_chunks
                



def check_filetype(filename):
    try:
        segments = filename.split(".")  
    except:
        dbext = False
    else:
        ext = segments[-1]
        if ext == "db":
            dbext = True
        else:
            dbext = False
    finally:
        return dbext



def get_absolutepath(path):
    try:
        db = os.path.abspath(path)
    except Exception as error:
        print(f"{error}")
    else:
        return db



def check_db(list):
    print("check db")
    print(list)



def create_db(list):
    print("create db")
    print(list)



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



errstring = {
    "invalid filetype": "supplied databased file does not end in .db",
    "input": "unrecognised input",
    "invalid name": "filenames must not include '/'",
    "unknown dir": "specified directory not found"
}



def aborting():
    sys.exit("Lollypop exiting...")



if __name__ == "__main__":
    main()

# https://www.youtube.com/watch?v=byHcYRpMgI4
# https://docs.python.org/3/library/sqlite3.html