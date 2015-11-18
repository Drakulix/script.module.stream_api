# Steam Streaming Client Library for Python

Currently not able to actually parse the video/audio stream or pass controls.
Only implemented until actual game start, but provides all necessary parameters to start the 'streaming_client' executable shipped with steam.
More is not the goal of this library, but is happily accepted as a pull request.

Minimum Python Version 2.6 (Kodi related). Not tested with python 3. Any pull requests fixing Python 3 compatibility without breaking Python >= 2.6 are happily accepted.

## Dependencies

protobuf
ssl_psk / common-ssl (https://github.com/webgravel/common-ssl)

## Example Usage

```python

import random
import time
from stream_api.discovery import DiscoveryClient
from stream_api.control import ControlClient
from stream_api.eresult import *
from stream_api import streaming_client

client_id = random.randrange(0, sys.maxint) #random id, yey
clients = dict()

def client_app_changed(instance): #instance is a tuple of hostname, username (only if those were set on the control_client obj, otherwise tuble of None or mixed)
    #we got any apps, lets start one
    client = clients[instance]
    client.send_start_stream(client.apps.keys()[0])

    #get status and reset
    status = self.connected_steam_instances[instance].stream_status
    self.connected_steam_instances[instance].stream_status = None

    if status.e_launch_result == k_EResultOK:
        streaming_client.run_client(self.connected_steam_instances[instance].ip, status.stream_port, status.auth_token)
    else:
        print status.e_launch_result

    client.stop()
    del clients[instance]

def client_found(addr, status):
    username = steam_config.username(status.users.steamid[0])
    auth = steam_config.shared_auth(status.users.steamid[0])

    control_client = control.ControlClient(addr, status.connect_port, auth, status.users[0].steamid, status.users[0].auth_key_id, client_id, client_app_changed, None)
    control_client._hostname = status.hostname
    control_client._username = username

    clients[(status.hostname, username)] = control_client

    control_client.start()

discovery_client = discover.DiscoveryClient(client_id, client_found)
discovery_client.start()

```
