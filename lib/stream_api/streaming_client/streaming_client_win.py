import os
import sys
import subprocess

from ..views import utils

pluginhandle = int(sys.argv[1])

def run_client(ip, port, auth_token):
    home = os.path.expanduser("~")
    my_env = os.environ.copy()
    my_env["Steam3Master"] = ip+":57343"

    f = None
    try:
        import xbmc
        #log everything (/tmp/streaming.log is not complete)
        f = open(os.path.join(xbmc.translatePath("special://profile/addon_data/"+addonID), "streaming.log"), "w")
    except:
        pass

    command_args = [os.environ["ProgramFiles"]+"\\Steam\\streaming_client.exe", "--server", ip+":"+str()]

    if options:
        command_args.extend(options)

    command_args.append(''.join(x.encode('hex') for x in auth_token))

    print command_args

    proc = subprocess.Popen(command_args, cwd=os.environ["ProgramFiles"]+"\\Steam\\", stdout=f, stderr=f, env=my_env)
    proc.wait()
