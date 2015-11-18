import os
import sys
import subprocess

#pluginhandle = int(sys.argv[1])

def run_client(ip, port, auth_token, options):
    home = os.path.expanduser("~")
    #stupid runtime, this took a while

    steam_folder = "ubuntu12_32"
    if not os.path.exists(home+"/.steam/"+steam_folder):
        steam_folder = "bin32"

    my_env = os.environ.copy()
    my_env["LD_LIBRARY_PATH"] = home+"/.steam/"+steam_folder+":"+home+"/.steam/"+steam_folder+"/panorama:"+home+"/.steam/"+steam_folder+"/steam-runtime/i386/lib/i386-linux-gnu:"+home+"/.steam/"+steam_folder+"/steam-runtime/i386/lib:"+home+"/.steam/"+steam_folder+"/steam-runtime/i386/usr/lib/i386-linux-gnu:"+home+"/.steam/"+steam_folder+"/steam-runtime/i386/usr/lib:/usr/lib/i386-linux-gnu"
    my_env["Steam3Master"] = ip+":57343"
    my_env["STEAM_RUNTIME"] = home+"/.steam/"+steam_folder+"/steam-runtime"

    f = None
    try:
        import xbmc
        #log everything (/tmp/streaming.log is not complete)
        f = open(os.path.join(xbmc.translatePath("special://profile/addon_data/"+addonID), "streaming.log"), "w")
    except:
        pass

    command_args = [home+"/.steam/"+steam_folder+"/streaming_client", "--server", ip+":"+str(port)]

    if options:
        command_args.extend(options)

    command_args.append(''.join(x.encode('hex') for x in auth_token))

    print command_args

    #finally
    proc = subprocess.Popen(command_args, cwd=home+"/.steam/", stdout=f, stderr=f, env=my_env)
    proc.wait()
