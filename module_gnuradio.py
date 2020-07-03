"""__author__ = "Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"""

import os
import sh
import pprint
import inspect
import logging
import subprocess
from enum import Enum
import xmlrpc.client


__author__ = "Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


""" tracking the state of the radio program """
class RadioProgramState(Enum):
    INACTIVE = 1
    RUNNING = 2
    PAUSED = 3
    STOPPED = 4


class GnuRadioModule(modules.DeviceModule, RadioNetDevice):
    """
        Basic GNURadio connector module.

        Supported functionality:
        - activate_radio_program: pass name of RP and the flowgraph
                                  as XML GRC file
        - deactivate_radio_program: stop or pause RP
        - set_parameters/get_parameters: generic getter/setter functions to
                                         control GnuRadio RP at runtime

        TODO: pass init parameters as parameters to python file;
              see gr802.11 as an example.
    """

    def __init__(self, usrp_addr="addr=192.168.30.2",
                 ctrl_socket_host="localhost",
                 ctrl_socket_port=8080):
        super(GnuRadioModule, self).__init__()

        self.log = logging.getLogger('GnuRadioModule')

        self.gr_radio_programs = {}
        self.gr_process = None
        self.gr_process_io = None
        self.gr_radio_programs_path = os.path.join(os.path.expanduser("~"), ".uniflex", "radio")
        if not os.path.exists(self.gr_radio_programs_path):
            os.makedirs(self.gr_radio_programs_path)
            self._build_radio_program_dict()

        # config values
        self.usrp_addr = usrp_addr
        self.ctrl_socket_host = ctrl_socket_host
        self.ctrl_socket_port = ctrl_socket_port
        self.ctrl_socket = None

        self.gr_state = RadioProgramState.INACTIVE

        self.log.debug('initialized ...')

    def activate_radio_program(self, grc_radio_program_name=None,
                               grc_program=None, iface=None):
        """
        Activates and starts a GNURadio program.
        :param grc_radio_program_name: name of the radio program to
                                       be activated; used for caching
        :param grc_program: the GRC XML radio program
        :return: True in case it was successful
        """
        self.log.info('activate_radio_program: %s' % grc_radio_program_name)

        if self.gr_state == RadioProgramState.INACTIVE:
            self.log.info("Start new radio program")
            self.ctrl_socket = None

            """Launches Gnuradio in background"""
            if grc_radio_program_name not in self.gr_radio_programs:
                # serialize radio program to local repository
                self._add_radio_program(grc_radio_program_name, grc_program)
                # rebuild radio program dictionary
                self._compile_radio_program(grc_radio_program_name)

            if self.gr_process_io is None:
                self.gr_process_io = {'stdout': open('/tmp/gnuradio.log', 'w+'), 'stderr': open('/tmp/gnuradio-err.log', 'w+')}

            if self.gr_process is not None:
                # An instance is already running
                self.gr_process.kill()
                self.gr_process = None

            try:
                # start GNURadio process
                pyRadioProgPath = os.path.join(self.gr_radio_programs_path, grc_radio_program_name + '.py')
                self.log.info("Start radio program: {}".format(pyRadioProgPath))
                self.gr_radio_program_name = grc_radio_program_name
                self.gr_process = subprocess.Popen(["env", "python2", pyRadioProgPath],
                                                   stdout=self.gr_process_io['stdout'], stderr=self.gr_process_io['stderr'])
                self.gr_state = RadioProgramState.RUNNING
            except OSError:
                return False
            return True

        elif self.gr_state == RadioProgramState.PAUSED and self.gr_radio_program_name == grc_radio_program_name:
            # wakeup
            self.log.info('Wakeup radio program')
            self._init_proxy()
            try:
                self.ctrl_socket.start()
                self.gr_state = RadioProgramState.RUNNING
            except xmlrpc.Fault as e:
                self.log.error("ERROR: %s" % e.faultString)
        else:
            self.log.warn('Please deactive old radio program before activating a new one.')

    def update_radio_program(self, grc_radio_program_name=None,
                             grc_program=None, iface=None):
        """
        Activates and starts a GNURadio program.
        :param grc_radio_program_name: name of the radio program
                                       to be activated; used for caching
        :param grc_program: the GRC XML radio program
        :return: True in case it was successful
        """
        self.log.fatal('On the fly updates are not yet supported.')
        raise exceptions.UnsupportedFunctionException(
            func_name=inspect.currentframe().f_code.co_name,
            err_msg='On the fly updates are not yet supported.')

    def deactivate_radio_program(self, grc_radio_program_name=None,
                                 do_pause=False):
        """
        Deactivates and stops a running GNURadio program.
        :param grc_radio_program_name: name of the radio program
                                       to be activated; used for caching
        :param do_pause: whether to just pause or to terminate
        :return: True in case it was successful
        """

        if self.gr_state == RadioProgramState.RUNNING or self.gr_state == RadioProgramState.PAUSED:

            if do_pause:
                self.log.info("pausing radio program")

                self._init_proxy()
                self.ctrl_socket.stop()
                self.ctrl_socket.wait()
                self.gr_state = RadioProgramState.PAUSED

            else:
                self.log.info("stopping radio program")

                if self.gr_process is not None and hasattr(self.gr_process, "kill"):
                    self.gr_process.kill()

                if self.gr_process_io is not None and self.gr_process_io is dict:
                    for k in self.gr_process_io.keys():
                        # if self.gr_process_io[k] is file and not self.gr_process_io[k].closed:
                        if not self.gr_process_io[k].closed:
                            self.gr_process_io[k].close()
                            self.gr_process_io[k] = None
                self.gr_state = RadioProgramState.INACTIVE
                # cleanup repo
                self._remove_radio_program(grc_radio_program_name)
        else:
            self.log.warn("no running or paused radio program; ignore command")

    def set_parameters(self, param_key_values):
        """ API call """
        if self.gr_state == RadioProgramState.RUNNING or self.gr_state == RadioProgramState.PAUSED:
            self._init_proxy()
            for k, v in param_key_values.items():
                try:
                    getattr(self.ctrl_socket, "set_%s" % k)(v)
                except Exception as e:
                    self.log.error("Unknown variable '%s -> %s'" % (k, e))
        else:
            self.log.warn("no running or paused radio program; ignore command")

    def get_parameters(self, param_key_list):
        """ API call """
        if self.gr_state == RadioProgramState.RUNNING or self.gr_state == RadioProgramState.PAUSED:
            rv = {}
            self._init_proxy()
            for k in param_key_list:

                try:
                    res = getattr(self.ctrl_socket, "get_%s" % k)()
                    rv[k] = res
                except Exception as e:
                    self.log.error("Unknown variable '%s -> %s'" % (k, e))
            return rv
        else:
            self.log.warn("no running or paused radio program; ignore command")
            return None

    """ Helper functions """

    def _add_radio_program(self, grc_radio_program_name,
                           grc_radio_program_code):
        """ API call: Serialize radio program to local repository """

        self.log.info("Add radio program %s to local repository" % grc_radio_program_name)

        # serialize radio program XML flowgraph to file
        fid = open(os.path.join(self.gr_radio_programs_path, grc_radio_program_name + '.grc'), 'w')
        fid.write(grc_radio_program_code)
        fid.close()

        # set USRP addr in XML flowgraph
        self.log.info('Replace usrp_addr variable in grc by %s' % self.usrp_addr)
        doc = xmlle.parse(os.path.join(self.gr_radio_programs_path, grc_radio_program_name + '.grc'))
        el_usrp_addr = doc.xpath('/flow_graph/block/key[text()="variable"]/../param/value[text()="usrp_addr"]/../../param/key[text()="value"]/../value')
        el_usrp_addr[0].text = '"' + self.usrp_addr + '"'
        doc.write(os.path.join(self.gr_radio_programs_path, grc_radio_program_name + '.grc'))

    def _remove_radio_program(self, grc_radio_program_name):
        """ API call: Remove radio program from local repository """

        if self.gr_radio_programs is not None and grc_radio_program_name in self.gr_radio_programs:
            os.remove(self.gr_radio_programs[grc_radio_program_name])
            os.rmdir(os.path.join(self.gr_radio_programs_path, grc_radio_program_name))
            os.remove(os.path.join(self.gr_radio_programs_path, grc_radio_program_name + '.grc'))

    def _compile_radio_program(self, grc_radio_program_name):
        grProgramPath = os.path.join(self.gr_radio_programs_path, grc_radio_program_name + '.grc')
        outdir = "--directory=%s" % self.gr_radio_programs_path
        print(grProgramPath)
        print(outdir)
        try:
            sh.grcc(outdir, grProgramPath)
        except Exception as e:
            raise
        self.log.info("Compilation Completed")

    def _build_radio_program_dict(self, grc_radio_program_name=None):
        """
            Converts the radio program XML flowgraphs
            into executable python scripts
        """
        self.gr_radio_programs = {}
        grc_files = dict.fromkeys([os.path.splitext(x)[0] for x in os.listdir(self.gr_radio_programs_path) if x.endswith(".grc")], 0)

        self.log.info('grc_files: %s' % str(grc_files))

        topblocks = dict.fromkeys([x for x in os.listdir(self.gr_radio_programs_path) if os.path.isdir(os.path.join(self.gr_radio_programs_path, x))], 0)

        self.log.info('topblocks: %s' % str(topblocks))

        for x in grc_files.keys():
            grc_files[x] = os.stat(os.path.join(self.gr_radio_programs_path, x + ".grc")).st_mtime
            try:
                os.mkdir(os.path.join(self.gr_radio_programs_path, x))
                topblocks[x] = 0
            except OSError:
                pass

        for x in topblocks.keys():
            topblocks[x] = os.stat(os.path.join(self.gr_radio_programs_path, x, x + '.py')).st_mtime if os.path.isfile(
                os.path.join(self.gr_radio_programs_path, x, x + '.py')) else 0

        self.log.info('topblocks2: %s' % str(topblocks))

        for x in grc_files.keys():
            if grc_files[x] > topblocks[x]:
                outdir = "--directory=%s" % os.path.join(self.gr_radio_programs_path, x)
                input_grc = os.path.join(self.gr_radio_programs_path, x + ".grc")
                self.log.info('Input to grc %s' % input_grc)
                try:
                    subprocess.check_call(["grcc", outdir, input_grc])
                except Exception as inst:
                    self.log.error('Failed to run grcc %s' % str(inst))
                    pass

        for x in topblocks.keys():
            if os.path.isfile(os.path.join(self.gr_radio_programs_path, x, x + '.py')):
                self.gr_radio_programs[x] = os.path.join(self.gr_radio_programs_path, x, x + '.py')

        self.log.info('gr_radio_programs:\n{}'.format(pprint.pformat(self.gr_radio_programs)))


    def _init_proxy(self):
        if self.ctrl_socket == None:
            self.ctrl_socket = xmlrpc.client.ServerProxy("http://%s:%d" % (self.ctrl_socket_host, self.ctrl_socket_port))