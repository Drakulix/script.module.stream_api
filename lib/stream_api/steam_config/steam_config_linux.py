import os

def auth_path(steamid32):
    return os.path.expanduser("~")+"/.steam/steam/userdata/"+str(steamid32)+"/config/localconfig.vdf"
