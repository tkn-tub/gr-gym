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
            if not os.path.exists(self.address):
                #os.remove(self.address)
                os.mkfifo(self.address, 0o666)
            pipein = open(self.address, 'rb')
            f = open("." + self.address + ".csv", "a")
            self.log.debug("open pipe")

            while not self.stop:
                buf = (pipein.read(structlen))
                if len(buf) == 0:
                    break
                #print("read data")
                tmp = np.frombuffer(buf, dtype=self.dtype)
                
                #for i in range(0,int(len(arr) / self.elements)):
                #tmp = arr[(i * self.elements) : (self.elements * (i+1))]
                f.write(str(self.interval) + "," + str(timer() - self.data[1]) + "\n")
                self.mutex.acquire()
                #self.prev = self.data
                self.data = (tmp, timer())
                self.mutex.release()
                self.waitevent.set()

            pipein.close()
            f.close()
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
