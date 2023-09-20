import os
import hashlib

def get_fullpath():
    path = os.getcwd()
    print(f"Lollypop starting from: {path}")
    #ignored files: for now we will always ignore .files no matter what, maybe in the future I can add something more sophisticated
    return path

def get_parent(path):
    segments = path.split("/")
    return segments[-1]

def get_md5sum(filepath):
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    md5sum = md5.hexdigest()
    return md5sum

def walk_path(path):
    for (root,dirs,files) in os.walk(path, topdown=True):
        for file in files:
            filepath = "/".join([root,file])
            parent = get_parent(root)
            md5sum = get_md5sum(filepath)
            print(f"{md5sum}, {filepath}, {parent}/{file}")

def main():
    fullpath = get_fullpath()
    walk_path(fullpath)
    #currentpath = get_current_path()
    #contents = get_dir_contents(currentpath)
    ##walking: set depth 0
    ##walking: use fullpath to get dir contents
    ##walking: 
    #outfile(contents)
    

if __name__ == "__main__":
    main()
