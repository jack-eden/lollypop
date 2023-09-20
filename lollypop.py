import os

def get_fullpath():
    path = os.getcwd()
    print(f"Lollypop starting from: {path}")
    #ignored files: for now we will always ignore .files no matter what, maybe in the future I can add something more sophisticated
    return path

def get_parent(path):
    segments = path.split("/")
    return segments[-1]

def walk_path(path):
    for (root,dirs,files) in os.walk(path, topdown=True):
        for file in files:
            parent = get_parent(root)
            print(f"{parent}/{file}, {root}/{file}")


def outfile(output):
    pass

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
