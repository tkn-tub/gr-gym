from timeit import default_timer as timer
import os
import threading
import xmlrpc.client
import numpy as np
import logging
import socket
import sys
from enum import Enum

class BridgeConnectionType(Enum):
    PIPE = 0
    UDP = 1
    TCP = 2

class CommunicationElement:
    def __int__(self, address):
        pass
    def read(self, structlen):
        pass
    def close(self):
        pass

class CommunicationPipe(CommunicationElement):
    def __int__(self, address):
        if not os.path.exists(address):
            os.mkfifo(address, 0o666)
        self.pipein = open(address, 'rb')
    def read(self, structlen):
        return self.pipein.read(structlen)
    def close(self):
        return self.pipein.close()

class CommunicationUDP(CommunicationElement):
    def __int__(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip, port = address.split(':')
        server_address = (ip, port)
        sock.bind(server_address)
    def read(self, structlen):
        return self.sock.recvfrom(structlen)[0]
    def close(self):
        return self.sock.close()

class CommunicationTCP(CommunicationElement):
    def __int__(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip, port = address.split(':')
        server_address = (ip, port)
        self.sock.connect(server_address)
    def read(self, structlen):
        return self.sock.recv(structlen)
    def close(self):
        return self.sock.close()

class PipeListener(threading.Thread):
    def __init__(self, address, mydtype, elements, comTyp=BridgeConnectionType.PIPE):
        threading.Thread.__init__(self) 
        self.dtype = np.dtype(mydtype)
        self.address = address
        self.elements = elements
        self.interval = 300
        self.stop = False
        self.data = np.zeros(shape=(self.elements,1))
        self.data = (self.data.astype(self.dtype), timer())
        #self.prev = self.data
        self.mutex = threading.Lock()
        self.log = logging.getLogger('PipeListener[' + self.address+ ']')
        self.waitevent = threading.Event()
        self.waitcounter_mutex = threading.Lock()
        self.waitcounter = 0
    
    # listen on pipe with address
    # create pipe if id does not exists
    # store data in buffer
    def run(self):
        structlen = self.dtype.itemsize * self.elements
        while not self.stop:
            if comTyp == BridgeConnectionType.PIPE:
                connection = CommunicationPipe(address)
            else if comTyp == BridgeConnectionType.UDP:
                connection = CommunicationUDP(address)
            else if comTyp == BridgeConnectionType.TCP:
                connection = CommunicationTCP(address)
            else:
                raise ValueError('Type of connection is unkown!')
            
            self.log.debug("open pipe")

            while not self.stop:
                buf = connection.read(structlen)
                if len(buf) == 0:
                    break
                #print("read data")
                tmp = np.frombuffer(buf, dtype=self.dtype)
                
                #for i in range(0,int(len(arr) / self.elements)):
                #tmp = arr[(i * self.elements) : (self.elements * (i+1))]
                #f.write(str(self.interval) + "," + str(timer() - self.data[1]) + "\n")
                self.mutex.acquire()
                #self.prev = self.data
                self.data = (tmp, timer())
                self.mutex.release()
                self.waitevent.set()

            connection.close()
            #f.close()
            self.waitevent.set()
    
    #return data from buffer
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
    def subscribe_parameter(self, name, address, dtype, elements):
        if name in self.pipes:
            raise Exception("There is already an parameter of this name")
            self.log.error("Parameter already exists '%s'" % (name))
        self.pipes[name] = PipeListener(address, dtype, elements)
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
    
    # return result of pipe if name exists there
    # otherwise forward request to rpc
    #def get_parameter_prev(self, name):
    #    if name in self.pipes:
    #        return self.pipes[name].get_prev()
    #    else:
    #        try:
    #            res = (getattr(self.rpc, "get_%s" % name)(), timer())
    #        except Exception as e:
    #            self.log.error("Unknown variable '%s -> %s'" % (name, e))
    #        return res

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
    
    #def set_interval(self, interval):
    #    for key, elem in self.pipes.items():
    #        elem.set_interval(interval)
