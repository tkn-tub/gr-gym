gr-gym
============

[OpenAI Gym](https://gym.openai.com/) is a toolkit for reinforcement learning (RL) 
widely used in research. Additionally, researcher are using 
[GNU Radio](https://www.gnuradio.org/) as Software Defined Radio (SDR) toolkit to 
do rapid and low cost prototyping of new wireless protocols. 
**GrGym** is a framework that integrates both OpenAI Gym and Gnu Radio in order 
to encourage usage of RL in communication networks research.

Installation
============

In order to run **GrGym** you need to install both OpenAI Gym and Gnu Radio. 
Moreover in order to run the 802.11p scenario you need to install additional 
Gnu Radio blocks.

##### 1. Install dependencies for Gnu Radio
```
# dependencies for Ubuntu 20.04:
sudo apt install git cmake g++ libboost-all-dev libgmp-dev swig python3-numpy \
python3-mako python3-sphinx python3-lxml doxygen libfftw3-dev \
libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev python3-pyqt5 \
liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins \
python3-zmq python3-scipy python3-gi python3-gi-cairo gobject-introspection gir1.2-gtk-3.0
```
See https://wiki.gnuradio.org/index.php/UbuntuInstall

##### 2. Install Gnu Radio from source
```
# install on Ubuntu 20.04:
cd ~/
sudo apt install git cmake g++ libboost-all-dev libgmp-dev swig python3-numpy python3-mako python3-sphinx python3-lxml doxygen libfftw3-dev libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev python3-pyqt5 liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins python3-zmq python3-scipy python3-pip python3-gi-cairo
pip3 install git+https://github.com/pyqtgraph/pyqtgraph@develop
pip3 install numpy scipy
echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export PYTHONPATH=/usr/local/lib/python3/dist-packages:usr/local/lib/python2.7/site-packages:$PYTHONPATH' >> ~/.profile
echo 'export LD_LIBRARY_PATH=/user/local/lib:$LD_LIBRARY_PATH' >> ~/.profile
cd ~/
git clone --recursive https://github.com/gnuradio/gnuradio
cd gnuradio
git checkout maint-3.8
mkdir build
cd build
git pull --recurse-submodules=on
git submodule update --init
cmake -DENABLE_GR_UHD=OFF ..
make -j $(nproc --all)
sudo make install
sudo ldconfig
```
see https://wiki.gnuradio.org/index.php/InstallingGR#From_Source

##### 3. Install additional Gnu Radio blocks for IEEE 802.11p scenario
```
cd ~/
git clone https://github.com/bastibl/gr-foo.git
cd gr-foo
mkdir build
cd build
cmake ..
make -j $(nproc --all)
sudo make install
sudo ldconfig

cd ~/
git clone git://github.com/bastibl/gr-ieee802-11.git
cd gr-ieee802-11
mkdir build
cd build
cmake ..
make -j $(nproc --all)
sudo make install
sudo ldconfig
```
See https://github.com/bastibl/gr-ieee802-11

##### 4. Install OpenAI Gym
```
# minimal install of the packaged version directly from PyPI:
sudo pip3 install gym

see https://github.com/openai/gym
```

##### 5. Install additional Gnu Radio blocks from **GrGym**
```
cd ~/gr-gym
cd ./examples/rl-wifi-rt/gr-grgym-ieee802-11/grgym
mkdir build
cd build
cmake ../
make -j $(nproc --all)
sudo make install
sudo ldconfig
```

##### 6. Install **GrGym** located in ./grgym (Python3 required)
```
cd ~/gr-gym
sudo pip3 install -e ./grgym
```

##### 7. (Optional) Install all libraries required by your agent 
(like tensorflow, keras, etc.).

```
pip3 install --upgrade pip
pip3 install tensorflow==2.3.1
pip3 install keras
```

Examples
========

All examples can be found [here](./examples/).

## Closed-loop ratecontrol for IEEE 802.11p
We consider the problem of rate adaptation (MCS selection) in 802.11p. 
In this example the agent can observe the channel state (RSSI per OFDM 
subcarrier) in order to adapt the MCS/rate for the subsequent data packets. 
This problem can be solved using the Actor Critic Method:
```
cd ./examples/rl-wifi-rt/agents/
python3 agentAC.py
```
Note, you have to compile the wifi_phy_hier.grc before:
```
grcc ./examples/rl-wifi-rt/gr-grgym-ieee802-11/wifi_phy_hier.grc
```
## How to create your own example
If you want to solve a new GNU Radio Problem with RL, you have to think about
1. the GNU-Radio programm (flow graph)
1. the RL model with
    1. Action and its format
    1. Observation and its format
    1. Reward
    1. Game over
1. the RL agent

In this document we do not give a guideline of how to write a GNU-Radio programm or a RL-Agent. We just concentrate on how **GrGym** can combine them.

### Basic Interface

##### 1. Example Python script. Note, that `gym.make('grgym:grenv-v0')` starts Gnu Radio program configured in the ./params/config.yaml file.
See below how to use **GrGym** as OpenAI-Gym environment. The `config_file` parameter is optional.
```
import gym
import MyAgent

env = gym.make('grgym:grenv-v0', config_file=pathToConfig)
obs = env.reset()
agent = MyAgent.Agent()

while True:
  action = agent.get_action(obs)
  obs, reward, done, info = env.step(action)

  if done:
    break
env.close()

```
##### 2. Any Gnu Radio program be used as a Gym environment. This requires only to create a Python class derived from GrScenario class and to implement the following functions:
```
def get_observation_space()
def get_action_space()
def execute_action(action)
def get_obs()
def get_reward()
def get_done()
def reset()
def get_info()
def sim_channel()   #optional
```
Create a new scenario file in the ./grgym/scenarios directory. Implement the RL-model within this file. Therefore, use the decribed interface. The interface is called from **GrGym** when handling the requests of the RL-agent. The method `sim_channel()` can be used for channel simulation. In this method you can describe, how the simulation have to change from step to step. If you do not have a chanel simulation, you can use an empty method there.

##### 3. Any Gnu Radio parameter and variable can be controlled by the generic **GrGym** communication interface `GR_Bridge`:
`GR_Bridge` is the generic communication to the GNU-Radio program **GrGym** comes with. It allows to read and to write a given variable within the GNU-Radio program. Via `GR_Bridge` listening on GNU-Radio data streams is possible, too. The module has the following methods:
```
bridge = GR_Bridge(rpcHost, rpcPort)
bridge.subscribe_parameter(name, address, dtype, elements, comtype)
value = bridge.get_parameter(name)
bridge.set_parameter(name, value)
bridge.wait_for_value(name)
```
Reading and writing to variables happens via XML-RPC calls. Therefore, you have to specify the address and the port of XMLRPC-Server when instantiating `GR_Bridge`. The XMLRPC-Server block has to be part of GNU-Radio program. In GNU-Radio there is a block for this task. Via `get_parameter()` and `set_parameter()`, all variables in the GNU-Radio program are now accessable by **GrGym**.

Data streams are not stored within a variable in GNU-Radio. To read them, the GNU-Radio program has to send them to **GrGym**. Different types of communication are possible:
- named pipes (`BridgeConnectionType.PIPE`)
- TCP (`BridgeConnectionType.TCP`)
- UDP (`BridgeConnectionType.UDP`)
- ZeroMQ (`BridgeConnectionType.ZMQ`)
Data streams can be forwarded into the related sink blocks in GNU-Radio. This makes them accessable for `GR_Bridge`. To listen to those traffic, you can use the `subscribe_parameter()` method. It takes an internal name, you want to address the value with. Next it takes the address of the traffic. This can be the network address and port of the packet traffic or the path of the named pipe. The `comtype` argument describes the type of communication. `GR_Bridge` listens to the traffic and shapes it into a `numpy` vector. The data type of this vector and its length have to be specifyed, too. `GR_Bridge` internal buffer and stores the last vector of each stream. The data can be read by taking `get_parameter()`. The name is the internal name, you gave at subscription. Note, multiple requests will return the same value.
`wait_for_value()` method does a blocking call until there is new data received on a given stream.

See the example scenario for rate control in IEEE 802.11p implemented 
in ./grgym/grgym/scenarios/ieee80211p_scenario.py

Contact
============
* Anatolij Zubow, TU-Berlin, zubow@tkn
* Sascha Roesler, TU-Berlin, s.roesler@campus
* Piotr Gawlowicz, TU-Berlin, gawlowicz@tkn
* tkn = tkn.tu-berlin.de
* campus = campus.tu-berlin.de

How to reference **GrGym**?
============

Please use the following bibtex :

TBD.
