import socket
import json
from threading import Timer
from _utils import catch_exception

class Socket:

    @catch_exception
    def __init__(self, ActionsBase):
        self.base = ActionsBase

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setblocking(0)

        self._local_addr = ('127.0.0.1', 9005)
        self._remote_addr = ('127.0.0.1', 9004)

        self.bind()

        def parse():
            self.process()
            self.base.canonical_parent.schedule_message(1, parse)
        parse()


    def bind(self):
        try:
            self._socket.bind(self._local_addr)
            self.log('Starting on: ' + str(self._local_addr) + ', remote addr: ' + str(self._remote_addr))
        except:
            msg = 'ERROR: Cannot bind to ' + str(self._local_addr) + ', port in use. Trying again...'
            self.log(msg)
            t = Timer(5, self.bind)
            t.start()


    def send(self, name, obj=None):
        def jsonReplace(o):
            return str(o)
        try:
            self._socket.sendto(json.dumps(
                {"event": name, "data": obj}, default=jsonReplace, ensure_ascii=False), self._remote_addr)
        except Exception, e:
            self._socket.sendto(json.dumps(
                {"event": "error", "data": str(type(e).__name__) + ': ' + str(e.args)}, default=jsonReplace, ensure_ascii=False), self._remote_addr)
            self.log("Socket Error " + name + "(" + str(uuid) + "): " + str(e))

    def process(self):
        try:
            while 1:
                data = self._socket.recv(65536)
                if len(data):
                    payload = json.loads(data)
                    self.input_handler(payload)
        except socket.error:
            return
        except Exception, e:
            self.log("Error: " + str(e.args))

    def input_handler(self, payload):
        # self.log(payload)
        if payload['event'] == 'get_state':
            state = self.base.get_state()
            self.send('give_state', state)

    def shutdown(self):
        self._socket.close()

    def log(self, msg):
        self.base.log(msg)