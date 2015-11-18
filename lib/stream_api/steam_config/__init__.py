from sys import platform as _platform
import os

if _platform == "linux" or _platform == "linux2":
    from .steam_config_linux import auth_path
elif _platform == "darwin":
    from .steam_config_osx import auth_path
elif _platform == "win32":
    from .steam_config_win import auth_path

import glob

class LocalSteamUserDoesNotExists(Exception):
     def __init__(self, userid):
         self.userid = userid

     def __str__(self):
         return "Local Steam User (id32: "+self.userid+") does not exist (log in at least once)"

def username(steamid64):
    return read_config(int(steamid64) - 76561197960265728)[0]

def shared_auth(steamid64):
    return read_config(int(steamid64) - 76561197960265728)[1]

def read_config(steamid32):
    config_file = auth_path(steamid32) #get os specific config path for authentication key
    if not os.path.exists(config_file):
        raise LocalSteamUserDoesNotExists(steamid32)

    #parse state
    next_auth = False

    #parse all configs
    username = ""
    shared_auth = None

    #parse line by line
    for line in open(config_file):
        #get username if encountered
        if "PersonaName" in line:
            username = line.split("\"")[3]
        #and auth
        if next_auth and "AuthData" in line:
            shared_auth = line.split("\"")[3]
            next_auth = False
        if "SharedAuth" in line:
            next_auth = True

    #match username for config file
    return (username, shared_auth)
