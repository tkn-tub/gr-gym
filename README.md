gr-gym
============

[OpenAI Gym](https://gym.openai.com/) is a toolkit for reinforcement learning (RL) widely used in research. Additionally, researcher are using [GNU Radio](https://www.gnuradio.org/) as Software Defined Radio (SDR) tool to do rapid and low cost prototyping of new and existing wired/wireless technologies. gr-gym is a framework that integrates both OpenAI Gym and Gnu Radio in order to encourage usage of RL in networking research.

Installation
============

In order to run gr-gym you need to install both OpenAI Gym and Gnu Radio. Moreover in order to run the 802.11p example you need additional Gnu Radio blocks.

1. Install dependencies for Gnu Radio
```
# dependencies for Ubuntu 20.04:
sudo apt install git cmake g++ libboost-all-dev libgmp-dev swig python3-numpy \
python3-mako python3-sphinx python3-lxml doxygen libfftw3-dev \
libsdl1.2-dev libgsl-dev libqwt-qt5-dev libqt5opengl5-dev python3-pyqt5 \
liblog4cpp5-dev libzmq3-dev python3-yaml python3-click python3-click-plugins \
python3-zmq python3-scipy python3-gi python3-gi-cairo gobject-introspection gir1.2-gtk-3.0

see https://wiki.gnuradio.org/index.php/UbuntuInstall
```

2. Install Gnu Radio from source on Ubuntu 20.04
```
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

see https://wiki.gnuradio.org/index.php/InstallingGR#From_Source
```

3. Install additional Gnu Radio blocks for IEEE 802.11p scenario
```
git clone https://github.com/bastibl/gr-foo.git
cd gr-foo
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

git clone git://github.com/bastibl/gr-ieee802-11.git
cd gr-ieee802-11
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

see https://github.com/bastibl/gr-ieee802-11
```

3. Install OpenAI Gym
```
# minimal install of the packaged version directly from PyPI:
pip3 install gym

see https://github.com/openai/gym
```

4. Install the Gnu Radio blocks from grgym
```
cd example/ieee802_11/gnuradio_blocks/grgym
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig
```

5. Install grgym located in ./grgym (Python3 required)
```
pip3 install -e ./grgym
```

6. (Optional) Install all libraries required by your agent (like tensorflow, keras, etc.).


Examples
========

All examples can be found [here](./example/agents/).

## Basic Interface

1. Example Python script. Note, that `gym.make('grgym:grenv-v0')` starts Gnu Radio program configured in the ./params/config.yaml file.
```
import gym
import MyAgent

env = gym.make('grgym:grenv-v0')
obs = env.reset()
agent = MyAgent.Agent()

while True:
  action = agent.get_action(obs)
  obs, reward, done, info = env.step(action)

  if done:
    break
env.close()

```
2. Any Gnu Radio program be used as a Gym environment. This requires only to create a Python class derived from gnu_case class and to implement the following functions:
```
def get_observation_space()
def get_action_space()
def execute_actions(action)
def get_obs()
def get_reward()
def get_done()
def reset()
def get_info()
```
Note, that the generic grgym interface allows to observe any variable or parameter in Gnu Radio.

See the example scenario for rate control in IEEE 802.11p implemented in ./grgym/grgym/scenarios/ieee80211codemodscenario.py

## Closed-loop ratecontrol for IEEE 802.11p
We consider the problem of rate adaptation (MCS selection) in 802.11p. In this example the agent can observe the channel state (RSSI per OFDM subcarrier) in order to adapt the MCS/rate for the subsequent data packets. This problem can be solved using the Actor Critic Method:
```
cd ./example/agents/
python3 agentAC.py
```

Contact
============
* Anatolij Zubow, TU-Berlin, zubow@tkn
* Sascha Roesler, TU-Berlin, s.roesler@campus
* tkn = tkn.tu-berlin.de
* campus = campus.tu-berlin.de

How to reference gr-gym?
============

Please use the following bibtex :

TBD.
