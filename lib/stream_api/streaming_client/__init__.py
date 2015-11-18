from sys import platform as _platform

if _platform == "linux" or _platform == "linux2":
    from .streaming_client_linux import *
elif _platform == "darwin":
    from .streaming_client_osx import *
elif _platform == "win32":
    from .streaming_client_win import *

#launching is different on every system
