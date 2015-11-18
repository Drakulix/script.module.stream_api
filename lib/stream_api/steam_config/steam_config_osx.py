import os

def auth_path(steamid32):
    return os.path.expanduser("~")+"/Library/Application Support/Steam/userdata/"+str(steamid32)+"/config/localconfig.vdf"
