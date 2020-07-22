# GR-Gym

This is a generic tool-kit to use GNU-Radio as OpenAI Gym environment. You can setup your own GNU-Radio scenario and define your ML model in the tool-kit.

## Getting Started

There are several tools required to run our project. Please follow the steps, to get it running on your machine.

### Prerequisites

There are several parts, you have to install first.
Please, first get and install OpenAI Gym. Perhaps, you should do the installation in a new virtual python environment. You find OpenAI Gym here: https://github.com/openai/gym
Next, you need an installation of GNU-Radio. For linux, you can use the official GNU-Radio packet repository. Here, you find information for the installation of GNU-Radio: https://wiki.gnuradio.org/index.php/UbuntuInstall
If you want to use the IEEE 802.11p example, you have to install the GNU-Radio blocks of Bastian Bloessl. See his github repository for the code and more information: https://github.com/bastibl/gr-ieee802-11

### Installing

Now, you have installed all required prequisites and you are ready to install our work. Therefore, please get our work:
```
git clone git@gitlab.tubit.tu-berlin.de:ali_alouane/GnuRadio_Gym.git
```

For the IEEE 802.11p scenario controlling the modulation and the coding rate, you have to install our extension blocks. Therefore, please do the following steps. You can choose whether you are using GNU-Radio 3.7 or GNU-Radio 3.8
```
cd example/ieee802_11/gnuradio_blocks/gr-gnugym
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig
```
You can also run the installation Skript in `example/ieee802_11/gnuradio_blocks/gr-gnugym`.

To install our OpenAI Gym environment, please do the following steps:

```
cd gnuRadio_env
pip install -e .
```

=======
### Bugfix for GNU-Radio 3.8
Our environment uses the `SimpleXMLRPCServer`. GNU-Radio could have a wrong yaml file for this function. Please open `/usr/share/gnuradio/grc/blocks/xmlrpc_server.block.yml` and change the module name to `xmlrpc.server`. Don't change the name of the class.

Yet, you are ready to use gnugym!

## Running the example

Now you are ready to do some testing. Perhaps, you want to start with our example? Before the agent can start, please compile `example/ieee802_11/gnuradio_blocks/wifi_phy_hier.grc` manually. Open the file with GNU-Radio-Companion (GRC) and click on the compile button. Now, your system is prepared to run the example. Therefore, please choose an agent and start it. You find some agents in `example/agents`. If the automatic execution is enabled in the configuration file, the environment will compile and start the `grc` file.
If you don't want to use the automatic compilation and startup, because the agent is on a separate machine, you have to start the GNU-Radio programm manually. Therefore, start GNU-Radio-Companion. Please open our example `.grc` file with GRC. You find it at `example/grc/wifi_loopback_w_fr_channel.grc`. If the environment requests the start of GRC, please click on the `Run` button in GRC. The start request of the environment is written in the agent window. Now, you can watch your agent at work.
Once, you used the `Run` button in GRC, there will be a python file of the example. You now can directly run the GNU-Radio example from your command line.

## Setting up an own scenario

### At GNU-Radio-Companion
If you want to create your own scenario, perhaps you should start with GRC. Please build your protocol stack within GRC. You should also think about the parameter, you want to control, the values, you need for your reward function and the values you need for your observation. For your parameter, please add a variable or a GUI block in your GRC sheet. Add the `XMLRPC-Server` block to make your parameter accessable. Configure the block by choosing a valid port number. For the variables, you need for reward and observation, please add a block which sends the variable to GNU-Radio. This can be a `File-Sink` block if you want to use named pipes. Activate the unbuffered option and choose the path to the future pipe for this variable. If you want to use a TCP connection, please add the `TCPServer-Sink` block. For UDP, please add the `UDP-sink` block to your flowchart.

### Describing your scenario
Create your scenario file in `gnuRadio_env/grgym/scenarios`. You have to implement the `gnu_case` interface. Therefore, you have to include 

```
from grgym.envs.gnu_case import gnu_case
```
The interface expects you to implement these functions:
- `__init__(self, gnuradio, args)`: Where gnuradio is the communication module, args are the arguments from the yaml file
- `get_observation_space(self)`: Returns the description of your observation
- `get_action_space(self)`: Returns the description of your action
- `execute_actions(self, action)`: Executes the given action (the action comes from the agent)
- `get_obs(self)`: Collects and returns the observation
- `get_reward(self)`: Calculates and returns the reward
- `get_done(self)`: Detects a game over and returs whether there is one
- `render(self)`: calls some rendering of the scenario (Most time not needed in GNU-Radio)
- `get_info(self)`: returns some human readable information to the agent (Most time not needed in GNU-Radio)
- `simulate(self)`: If you want to change simulation values in your GNU-Radio scenario, you can implement the changes here

To do the communication to GNU-Radio, you can use the `gnuradio` object. It is of type `GR-Brigde` and provides some helpful methods:
- `self.gnuradio.subscribe_parameter('gr_var', 'path/to/pipe' or 'server:port', numpy type of var, length of array, type of connection)`: If you want to listen to a variable, you should tell the `GR-Bridge` that it has to listen on it. Please specify, how to read the data via `numpy.dtype` and the length of the array. `GR-Bridge` will buffer the last value for you. Perhaps, you should specify the type (`BridgeConnectionType.PIPE`, `BridgeConnectionType.TCP`, `BridgeConnectionType.UDP`). The pipe is the default type. If the pipe does not exists, `GR-Bridge` will create it. For pipes is necessary to call this method before you start GNU-Radio. Otherwise, GNU-Radio will create a file and the communication will break.
- `(value, timestamp) = self.gnuradio.get_parameter('gr_var')`: Using get parameter, you can read a variable from GNU-Radio. If you are listening to the variable, you get the last value of the pipe via this method. You get the timestamp, when the data arrived at `GR-Bridge`, too. If there is no subscibtion for the variable, `GR-Bridge` uses the XMLRPC connection to read the data from GNU-Radio.
- `self.gnuradio.set_parameter('gr_var', value)`: You can set a value to a variable of a GNU-Radio GUI block or a variable block via this method.
- `self.gnuradio.wait_for_value(self, 'gr_var')`: You can wait for the next received data by calling this method.

### Changing the configuration file
Via the configuration file `params/config.conf` you can configure the environment and your scenario model. For the generic part, you can set:
- `radio_programs_compile_execute`: Enable or disable compilation of the `grc` file at initialisation of the environment
- `radio_programs_path`: Set the path where the GNU-Radio flowcharts (`.grc` files) are located
- `gnu_radio_program_filename`: Name of the GNU-Radio flowchart (`.grc`file)
- `gnu_radio_program`: Name of the GNU-Radio programm. It is equal to the programm name in GRC. It is defined in the top block of the flowchart.
- `scenario`: The module and the class of your specific scenario environment
- `rpchost`: Server address of the GNU-Radio XMLRPC-Server
- `rpcport`: Port number of the GNU-Radio XMLRPC-Server
- `eventbased`: Enable event based mode. Now your specific environment is responsible for waiting for new data. If disabled you run in timed mode. Then `stepTime` and `simTime` are used. The environment will block for the two time intervals.
- `stepTime`: Duration of time the environment has to wait between execution of an action and the collection of the reward
- `simulate`: Enable or disable the execution of the `simulate` methode
- `simTime`: Duration of time the environment has to wait between changing the simulation and the collection of the observation

For our IEEE 802.11p scenario, you can configure:
- `simSteps`: Number of steps with equal simulation (no change of simulation parameter within these number of steps)
- `simDistMin`: Minimum distance between sender and receiver in dB
- `simDistMax`: Maximum distance between sender and receiver in dB
- `maxRewardLoss`: Number of steps without a reception of a packet. If there in no packet within these steps, the environment will set `done` to `True`
- `modelSNR`: Set amplification of the simulated antenna
- `packetInterval`: Interval in ms between the generation of two consecutive packets.

## Writing your agent

To implement your own agent, you have to follow OpenAI Gym implementation rules. First, you have to import gym
```
import gym
```
Next you have to specify the environment (`'grgym:grenv-v0'`) in this case and you have to reset the environment.
```
env = gym.make('grgym:grenv-v0')
obs = env.reset()
```
Now you are able to get the description of action and observation space:
```
ac_space = env.action_space
ob_space = env.observation_space
```
You can use this information to run your agent. In the core of your agent, you have to use the `step` method to do one step. This step executes an action and returns observation, reward, done and some information.
```
obs, reward, done, info = env.step(int(action))
```

## Authors

* **Ali Alouane** (ali.alouane@campus.tu-berlin.de)
* **Sascha Rösler** (s.roesler@campus.tu-berlin.de)
* **Tien Dat Phan** (t.phan@campus.tu-berlin.de)

## License

This project is licensed under the MIT License

## Acknowledgments

* This is a student project of TU Berlin
* Thanks to our supervisor Dr. Anatolij Zubow
* and the complete TKN Group.
