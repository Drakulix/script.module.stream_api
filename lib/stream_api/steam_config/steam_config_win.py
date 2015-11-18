import os

def auth_path(steamid32):
    return os.environ["ProgramFiles"]+"\\Steam\\userdata\\"+str(steamid32)+"\\config\\localconfig.vdf"
