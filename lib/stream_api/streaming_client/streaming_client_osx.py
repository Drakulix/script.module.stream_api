import os
import sys
import subprocess

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

    command_args = ["/Applications/Steam.app/Contents/MacOS/streaming_client", "--server", ip+":"+str()]

    if options:
        command_args.extend(options)

    command_args.append(''.join(x.encode('hex') for x in auth_token))

    print command_args

    proc = subprocess.Popen(command_args, cwd="/Applications/Steam.app/Contents/MacOS/", stdout=f, stderr=f, env=my_env)
    proc.wait()
