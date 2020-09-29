'''
gnugym project, TU-Berlin 2020
Sascha Rösler <s.roesler@campus.tu-berlin.de>
Anatolij Zubow <zubow@tkn.tu-berlin.de>
'''

from timeit import default_timer as timer
import os
import threading
import xmlrpc.client
import numpy as np
import logging
import socket
import sys
import time
from enum import Enum
import zmq
from thread import start_new_thread

class BridgeConnectionType(Enum):
    PIPE = 0
    UDP = 1
    TCP = 2
    ZMQ = 3

class AbstractCommunicationElement:
    def __init__(self):
        pass
    def read(self, structlen):
        pass
    def close(self):
        pass

class CommunicationPipe(AbstractCommunicationElement):
    def __init__(self, address):
        super().__init__()
        if not os.path.exists(address):
            os.mkfifo(address, 0o666)
        self.pipein = open(address, 'rb')

    def read(self, structlen):
        return self.pipein.read(structlen)

    def close(self):
        return self.pipein.close()

class CommunicationUDP(AbstractCommunicationElement):
    def __init__(self, address):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip, port = address.split(':')
        port = int(port)
        server_address = (ip, port)
        self.sock.bind(server_address)

    def read(self, structlen):
        return self.sock.recvfrom(structlen)[0]

    def close(self):
        return self.sock.close()

class CommunicationZMQ(AbstractCommunicationElement):
    def __init__(self, address):
        super().__init__()
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.SUB)
        self.sock.connect(address)
        self.sock.setsockopt(zmq.SUBSCRIBE, b"")

    def read(self, structlen):
        return self.sock.recv()

    def close(self):
        return self.sock.close()

class CommunicationTCP(AbstractCommunicationElement):
    def __init__(self, address):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip, port = address.split(':')
        port = int(port)
        server_address = (ip, port)
        error = True
        while error:
            try:
                self.sock.connect(server_address)
                error = False
            except Exception:
                time.sleep(0.1)
        mystr = "connected"
        self.sock.send(mystr.encode())

    def read(self, structlen):
        return self.sock.recv(structlen)

    def close(self):
        return self.sock.close()

datalock = threading.Lock()
dataPipe = []
dataZMQ = []
stop = False
loggerfile = open("comlog.csv", "a")

def listenPipe:
    structlen = np.int32 #* self.elements
    while not stop:
        connection = CommunicationPipe('/tmp/grpipe')
        #connection = CommunicationZMQ(self.address)

        while not self.stop:
            buf = connection.read(structlen)
            if len(buf) == 0:
                break
            
            tmp = np.frombuffer(buf, dtype=np.int32)
            
            datalock.acquire()
            
            dataPipe.append(tmp)
            while len(dataZMQ) > 0 and len(dataPipe) > 0:
                pipe = dataPipe.pop(0)
                zmq = dataZMQ.pop(0)
                loggerfile.write(str(pipe) + ", " +  str(zmq))
            datalock.release()

        connection.close()

def listenZMQ:
    structlen = np.int32 #* self.elements
    while not stop:
        #connection = CommunicationPipe(self.address)
        connection = CommunicationZMQ('127.0.0.1:8021')

        while not self.stop:
            buf = connection.read(structlen)
            if len(buf) == 0:
                break
            
            tmp = np.frombuffer(buf, dtype=np.int32)
            
            datalock.acquire()
            
            dataZMQ.append(tmp)
            while len(dataZMQ) > 0 and len(dataPipe) > 0:
                pipe = dataPipe.pop(0)
                zmq = dataZMQ.pop(0)
                loggerfile.write(str(pipe) + ", " +  str(zmq))
            datalock.release()

        connection.close()

start_new_thread(listenPipe,())
start_new_thread(listenZMQ,())

'''
class PipeListener(threading.Thread):
    def __init__(self, address, mydtype, elements, comTyp=BridgeConnectionType.PIPE):
        threading.Thread.__init__(self) 
        self.dtype = np.dtype(mydtype)
        self.address = address
        self.elements = elements
        self.interval = 300
        self.stop = False
        self.data = []
        self.mutex = threading.Lock()
        self.log = logging.getLogger('PipeListener[' + self.address+ ']')
        self.waitevent = threading.Event()
        self.waitcounter_mutex = threading.Lock()
        self.waitcounter = 0
        self.comTyp = comTyp
        
    
    # listen on pipe with address
    # create pipe if id does not exists
    # store data in buffer
    def run(self):
        structlen = self.dtype.itemsize * self.elements
        while not self.stop:
            if self.comTyp == BridgeConnectionType.PIPE:
                connection = CommunicationPipe(self.address)
            elif self.comTyp == BridgeConnectionType.UDP:
                connection = CommunicationUDP(self.address)
            elif self.comTyp == BridgeConnectionType.TCP:
                connection = CommunicationTCP(self.address)
            elif self.comTyp == BridgeConnectionType.ZMQ:
                connection = CommunicationZMQ(self.address)
            else:
                raise ValueError('Type of connection is unkown! ' + str(self.comTyp))
            
            self.log.debug("open pipe")

            while not self.stop:
                buf = connection.read(structlen)
                if len(buf) == 0:
                    break
                
                tmp = np.frombuffer(buf, dtype=self.dtype)
                
                self.mutex.acquire()
                
                self.data.append(tmp)
                self.mutex.release()
                self.waitevent.set()

            connection.close()
            self.waitevent.set()
    
    # return data from buffer
    def get_data(self):
        self.mutex.acquire()
        tmp = self.data
        self.mutex.release()
        return tmp
    
    def set_stop(self):
        self.stop = True
    
    #def set_interval(self, interval):
    #    self.interval = interval
    
    def wait_for_value(self):
        if not self.stop:
            self.waitcounter_mutex.acquire()
            self.waitcounter += 1
            self.waitcounter_mutex.release()
            self.waitevent.wait()
            self.waitcounter_mutex.acquire()
            self.waitcounter -= 1
            if self.waitcounter <= 0:
                self.waitcounter = 0
                self.waitevent.clear()
            self.waitcounter_mutex.release()

class GR_Bridge:
    # create RPC procxy
    def __init__(self, rpcAddress, rpcPort):
        self.pipes = {}
        self.rpc = xmlrpc.client.ServerProxy("http://" + rpcAddress + ":" + str(rpcPort) + "/")
        self.log = logging.getLogger('GR-Bridge')
    
    # create thread to listen on pipe
    # add thread to pipe
    def subscribe_parameter(self, name, address, dtype, elements, comTyp=BridgeConnectionType.PIPE):
        if name in self.pipes:
            raise Exception("There is already an parameter of this name")
            self.log.error("Parameter already exists '%s'" % (name))
        self.pipes[name] = PipeListener(address, dtype, elements,comTyp)
        self.pipes[name].start()
    
    # return result of pipe if name exists there
    # otherwise forward request to rpc
    def get_parameter(self, name):
        if name in self.pipes:
            return self.pipes[name].get_data()
        else:
            try:
                res = (getattr(self.rpc, "get_%s" % name)(), timer())
            except Exception as e:
                self.log.error("Unknown variable '%s -> %s'" % (name, e))
            return res

    # set parameter via rpc
    def set_parameter(self, name, value):
        try:
            getattr(self.rpc, "set_%s" % name)(value)
        except Exception as e:
            self.log.error("Unknown variable '%s -> %s'" % (name, e))
    
    # send start via rpc
    def start(self):
        self.rpc.start()
    
    def close(self):
        for key, elem in self.pipes.items():
            elem.set_stop()
    
    def wait_for_value(self, name):
        if name in self.pipes:
            self.pipes[name].wait_for_value()
'''
