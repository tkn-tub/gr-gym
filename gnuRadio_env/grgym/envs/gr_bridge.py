from timeit import default_timer as timer
import os
import threading
import xmlrpc.client
import numpy as np
import logging

class PipeListener(threading.Thread):
    def __init__(self, address, mydtype, elements):
        threading.Thread.__init__(self) 
        self.dtype = np.dtype(mydtype)
        self.address = address
        self.elements = elements
        self.data = np.zeros(shape=(self.elements,1))
        self.data = (self.data.astype(self.dtype), timer())
        #self.prev = self.data
        self.mutex = threading.Lock()
    
    # listen on pipe with address
    # create pipe if id does not exists
    # store data in buffer
    def run(self):
        structlen = self.dtype.itemsize * self.elements
        while True:
            if not os.path.exists(self.address):
                #os.remove(self.address)
                os.mkfifo(self.address, 0o666)
            pipein = open(self.address, 'rb')
            f = open("." + self.address, "a")
            print("open pipe")

            while True:
                buf = (pipein.read(structlen))
                if len(buf) == 0:
                    print(buf)
                    break
                #print("read data")
                tmp = np.frombuffer(buf, dtype=self.dtype)
                
                #for i in range(0,int(len(arr) / self.elements)):
                #tmp = arr[(i * self.elements) : (self.elements * (i+1))]
                f.write(str(tmp) + ";\n")
                self.mutex.acquire()
                #self.prev = self.data
                self.data = (tmp, timer())
                self.mutex.release()

            pipein.close()
            f.close()
    
    #return data from buffer
    def get_data(self):
        self.mutex.acquire()
        tmp = self.data
        self.mutex.release()
        return tmp
    
    #def get_prev(self):
    #    self.mutex.acquire()
    #    tmp = self.prev
    #    self.mutex.release()
    #    return tmp

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

