import socket
import struct
import ssl
import ssl_psk
import sys
import time
import threading

import steammessages_remoteclient_pb2
import steammessages_remoteclient_discovery_pb2
import eresult

#magic at the start of every message
_vt01_magic = "VT01".encode("utf-8")

class ControlClient(object):

    #private variables
    _s = None #socket
    _running = False #run state (control via start/stop)
    _t = None #read thread
    _t_ping = None #ping thread
    _disconnect_callback = None
    _on_app_change_callback = None
    #connection parameters
    _steamid = None
    _auth_key_id = None
    _client_id = None
    _addr = None
    _port = None

    #callback only stuff
    _hostname = ""
    _username = ""

    #public variables
    apps = dict() #contains up to date app_state infos (see parsing below)
    authenticated = False #authentication_state, better try nothing before we are authenticated
    stream_status = None #status of a launched steam (poll for this after send_start_stream(), yes I know this is ugly, but i am lazy and this is async)
    ip = None #ip for later use


    def __init__(self, addr, port, auth, steamid, auth_key_id, client_id, on_app_change_callback=None, disconnect_callback=None):
        #connect via ssl_psk
        self._addr = addr
        self._port = port
        s_tmp = socket.socket()
        s_tmp.connect((addr, port))
        self._psk = auth.decode('hex')
        self._s = ssl_psk.wrap_socket(s_tmp, psk=self._psk, ciphers='PSK-AES128-CBC-SHA', ssl_version=ssl.PROTOCOL_TLSv1_2)
        self._s.settimeout(60.0)
        self._disconnect_callback = disconnect_callback
        self._on_app_change_callback = on_app_change_callback

        #set auth vars and others
        self._steamid = steamid
        self._auth_key_id = auth_key_id
        self._client_id = client_id
        self.ip = addr

        super(ControlClient, self).__init__()

    def _run_read(self):
        while self._running:
            #better catch, this is threaded again
            try:
                self._handle_message()
            #catch disconnect
            except struct.error:
                if self._running:
                    self.stop()
            except:
                  import traceback
                  traceback.print_exc()

    def _run_ping(self):
        while self._running:
            #better catch, this is threaded again
            try:
                self._send_ping()
                time.sleep(10)
            except:
                  import traceback
                  traceback.print_exc()

    def start(self):
        if self._running:
            return

        #lets do this
        self._running = True

        #authenticate
        self._send_auth()

        #and start reading
        self._t = threading.Thread(target=self._run_read)
        self._t.daemon = True
        self._t.start()

        self._t_ping = threading.Thread(target=self._run_ping)
        self._t_ping.daemon = True
        self._t_ping.start()

    def stop(self):
        if not self._running:
            return

        self._running = False
        self._s.close()

        #let handler cleanup (if it wants)
        if self._disconnect_callback != None:
            self._disconnect_callback(self)

    def reconnect(self, client_id):
        if not self._running:
            return

        self._running = False
        self._s.close()
        self._t.join()
        self._t_ping.join()

        self.authenticated = False

        #connect via ssl_psk
        s_tmp = socket.socket()
        s_tmp.connect((self._addr, self._port))
        self._s = ssl_psk.wrap_socket(s_tmp, psk=self._psk, ciphers='PSK-AES128-CBC-SHA', ssl_version=ssl.PROTOCOL_TLSv1_2)
        self._s.settimeout(60.0)

        self._client_id = client_id
        self.start()

    def _send_auth(self):
        message = steammessages_remoteclient_pb2.CMsgRemoteClientAuth()
        message.client_id = self._client_id

        status = message.status
        status.version = 6
        status.min_version = 6
        status.connect_port = 27036
        status.hostname = socket.gethostname()
        status.enabled_services = 0
        status.ostype = -203 #should we use this? this value should(!) be linux
        status.is64bit = True #is that any important?
        status.euniverse = 1
        status.timestamp = int(time.time())

        user = status.users.add()
        user.steamid = self._steamid
        user.auth_key_id = self._auth_key_id #same authentication, bloddy hacky, but we have no other key

        self._send_message(9500, message)

    def _send_auth_response(self, result):
        message = steammessages_remoteclient_pb2.CMsgRemoteClientAuthResponse()
        message.eresult = result
        self._send_message(9501, message)

    def send_start_stream(self, gameid, gamepads=None):
        message = steammessages_remoteclient_pb2.CMsgRemoteClientStartStream()
        if gameid != None:
            message.app_id = gameid
        message.environment = 1 #start in bigpicture (thats the goal, not working or doing anything right now)
        if gamepads != None:
            message.gamepad_count = gamepads
        try:
            self._send_message(9503, message)
        except:
            return None

    def _send_message(self, emsg, message):
        length = struct.pack("<i", message.ByteSize() + 8)
        emsg_data = struct.pack("<I", emsg | 0x80000000)
        legacy_header = struct.pack("<i", 0)
        message_data = message.SerializeToString()
        try:
            self._s.send(length + _vt01_magic + emsg_data + legacy_header + message_data)
        except:
            self.stop()

    def _send_ping_response(self):
        self._send_message(9506, steammessages_remoteclient_pb2.CMsgRemoteClientPingResponse())

    def _send_ping(self):
        self._send_message(9505, steammessages_remoteclient_pb2.CMsgRemoteClientPing())

    def _handle_message(self):
        length = struct.unpack("<i", self._s.recv(4))[0]
        if self._s.recv(4) != _vt01_magic:
            raise ConnectionError()
        emsg = struct.unpack("<I", self._s.recv(4))[0] & 0x7fffffff
        legacy_length = struct.unpack("<i", self._s.recv(4))[0] #do not try to parse it, if it is non null. there is no header
        message_data = self._s.recv(length - 8)

        message = None
        if emsg == 9500:
            message = steammessages_remoteclient_pb2.CMsgRemoteClientAuth()
            message.ParseFromString(message_data)
            self._send_auth_response(eresult.k_EResultOK)
        elif emsg == 9501:
            message = steammessages_remoteclient_pb2.CMsgRemoteClientAuthResponse()
            message.ParseFromString(message_data)
            if message.eresult == eresult.k_EResultOK:
                self.authenticated = True
        elif emsg == 9502:
            message = steammessages_remoteclient_pb2.CMsgRemoteClientAppStatus()
            message.ParseFromString(message_data)

            for app in message.status_updates: #app updates!
                changes = False
                if not app.app_id in self.apps:
                    self.apps[app.app_id] = dict()
                    changes = True
                if app.app_state != None:
                    self.apps[app.app_id]["state"] = app.app_state
                    changes = app.app_state == 4 or app.app_state == 8 or app.app_state == 64
                if app.update_info != None:
                    self.apps[app.app_id]["bytes_downloaded"] = app.update_info.bytes_downloaded
                    self.apps[app.app_id]["bytes_to_download"] = app.update_info.bytes_to_download
                    self.apps[app.app_id]["estimated_seconds_remaining"] = app.update_info.estimated_seconds_remaining
                if app.shortcut_info.name != None and app.shortcut_info.name != "":
                    self.apps[app.app_id]["name"] = app.shortcut_info.name
                    self.apps[app.app_id]["is_steam_game"] = False
                if changes:
                    if self._on_app_change_callback != None:
                        self._on_app_change_callback((self._hostname, self._username))

        elif emsg == 9503:
            message = steammessages_remoteclient_pb2.CMsgRemoteClientStartStream()
            message.ParseFromString(message_data)
            #what?
        elif emsg == 9504:
            message = steammessages_remoteclient_pb2.CMsgRemoteClientStartStreamResponse() #yey! got it!
            message.ParseFromString(message_data)
            self.stream_status = message
        elif emsg == 9505:
            message = steammessages_remoteclient_pb2.CMsgRemoteClientPing()
            message.ParseFromString(message_data)
            self.send_ping_response()
        else:
            pass
