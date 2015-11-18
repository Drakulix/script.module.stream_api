import random
import socket
import struct
import time
import threading
import sys
try:
    import xbmc
except:
    import time as xbmc

import steammessages_remoteclient_discovery_pb2

_packet_magic = struct.pack("=BBBBBBBB",  0xFF, 0xFF, 0xFF, 0xFF, 0x21, 0x4C, 0x5F, 0xA0) #discovery packet_magic

class DiscoveryClient(object):

    _s = None
    _sequenz_num = 0 #increasing sequenz_num
    _running = False
    _t1 = None
    _t2 = None

    discovered_steam_instances = dict()
    _callback = None

    def __init__(self, client_id, callback=None):
        try:
            self._own_address = xbmc.getIPAddress()
        except:
            self._own_address = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

        # open discovery udp socket
        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._s.bind(('', 27036)) # apperently not necessary
        self._client_id = client_id
        self._callback = callback
        super(DiscoveryClient, self).__init__()

    def _run_write(self):
        while self._running:
            try:
                self._send_discover_message()
                xbmc.sleep(3000)
            except:
                  import traceback
                  traceback.print_exc()

    def _run_read(self):
        while self._running:
            try:
                self._receive_response()
                xbmc.sleep(1) #seems to result in better thread scheduling
            except:
                  import traceback
                  traceback.print_exc()

    def start(self):
        if self._running:
            return

        self._running = True

        self._t1 = threading.Thread(target=self._run_write)
        self._t1.daemon = True
        self._t1.start()

        self._t2 = threading.Thread(target=self._run_read)
        self._t2.daemon = True
        self._t2.start()

    def stop(self):
        if not self._running:
            return

        self._running = False
        self._s.close()

    def _send_discover_message(self):
        # construct protobuf header
        header = steammessages_remoteclient_discovery_pb2.CMsgRemoteClientBroadcastHeader()
        header.client_id = self._client_id
        header.msg_type = 0
        #data and length
        header_data = header.SerializeToString()
        header_length = struct.pack("<i", header.ByteSize())

        # construct protobuf body
        body = steammessages_remoteclient_discovery_pb2.CMsgRemoteClientBroadcastDiscovery()
        self._sequenz_num+=1
        body.seq_num = self._sequenz_num
        #data and length
        body_data = body.SerializeToString()
        body_length = struct.pack("<i", body.ByteSize())

        # discover!
        self._s.sendto(_packet_magic + header_length + header_data + body_length + body_data, ('255.255.255.255', 27036))

    def _receive_response(self):
        try:
            (instance, addr) = self._s.recvfrom(1024)

            if instance.startswith(_packet_magic):
                instance_new = instance.split(_packet_magic, 2)[1]
                header_length = struct.unpack("<i", instance_new[:4])[0]
                header = instance_new[4:4+header_length]
                body_length = struct.unpack("<i",instance_new[4+header_length:8+header_length])[0]
                body = instance_new[8+header_length:8+header_length+body_length]

                #continue to parse header and body
                header_message = steammessages_remoteclient_discovery_pb2.CMsgRemoteClientBroadcastHeader()
                header_message.ParseFromString(header)

                if header_message.msg_type == 1:
                    #status message
                    body_message = steammessages_remoteclient_discovery_pb2.CMsgRemoteClientBroadcastStatus()
                    body_message.ParseFromString(body)
                    #print body_message

                    if addr[0] != self._own_address:
                        if not self.discovered_steam_instances.has_key(addr[0]):
                            self.discovered_steam_instances[addr[0]] = body_message
                        self._callback(addr[0], body_message)
                else:
                    #quit message
                    if self.discovered_steam_instances.has_key(addr[0]):
                        del self.discovered_steam_instances[addr[0]]
                return True

        except:
            pass

        return False
