import os

dirs = [
    "js",
    "js/collections",
    "js/models",
    "js/routers",
    "js/views"
]

def exists(p):
    try:
        os.stat(p)
        return True
    except:
        return False

def make_dirs():
    for d in dirs:
        print(d)
        os.chdir("/www")
        path = d.split('/')
        print(path)
        for p in path:
            if not exists(p):
                os.mkdir(p)
            os.chdir(p)
