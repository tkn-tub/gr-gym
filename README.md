# GR-Gym

This is a generic tool-kit to use GNU-Radio as OpenAI-Gym environment. You can setup your own GNU-Radio scenario and define your ML model in the tool-kit.

## Getting Started

There are several tools required to run our project. Please follow the steps, to get it running on your machine.

### Prerequisites

There are several parts, you have to install.
Please, first get and install OpenAI gym. Perhaps, you should do the installation in a new virtual python environment. You find OpenAI gym here: https://github.com/openai/gym
Next, you need an installation of GNU-Radio. For linux, you can use the official GNU-Radio packet repository. We are using GNU-Radio 3.7.11. Here, you find information for the installation of GNU-Radio: https://wiki.gnuradio.org/index.php/UbuntuInstall
If you want to use the IEEE 802.11p example, you have to install the GNU-Radio blocks of Bastian Bloessl. See his github repository for the code and more information: https://github.com/bastibl/gr-ieee802-11

### Installing

Now, you have installed all required prequisites and you are ready to install our work. Therefore, please get our work:
```
git clone git@gitlab.tubit.tu-berlin.de:ali_alouane/GnuRadio_Gym.git
```

For the IEEE 802.11p scenario controlling the modulation and the coding rate, you have to install our extension blocks. Therefore, please do the following steps
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

To install our OpenAI gym environment, please do the following steps:

```
cd gnuRadio_env
pip install -e .
```

No you are ready to use the gr-env!

## Running the example

Now you are ready to do some testing. Perhaps, you want to start with our example? Therefore, please choose an agent and start it. You find some agents in `example/agents`. If the automatic execution is enabled, the environment will compile and start the `grc` file.
If you don't want to use the automatic compilation and startup, because the agent is on a separate machine, you have to start the GNU-Radio programm manually. Therefore, start GNU-Radio-Companion (GRC). Please open our example `.grc` file with GRC. You find it at `example/grc/wifi_loopback_w_fr_channel.grc`. If the environment requests the start of GRC please t click on the `Run` button in GRC. The request of the environment is written in the agent window. Now, you can watch your agent at work.
Once, you used the `Run` button in GRC, there will be a python file of the example. You now can directly run the GNU-Radio example from your command line.

## Setting up an own scenario

### At GNU-Radio-Companion
If you want to create your own scenario, perhaps you should start with GRC. Please build your protocol stack within GRC. You should also think about the parameter, you want to control, the values, you need for your reward function and the values you need for your observation. For your parameter, please add a variable or a GUI block in your GRC sheet. Add the `XMLRPC-Server` block to make your parameter accessable. Configure the block by choosing a valid port number. For the variables, you need for reward and observation, please add a block which sends the variable to GNU-Radio. This can be a `File-Sink` block if you want to use named pipes. Activate the unbuffered option and choose the path to the future pipe for this variable. If you want to use a TCP connection, please add the `TCPServer-Sink` block. For UDP, please add the `UDP-sink` block to your flowchart.

### Describing your scenario
Create your scenario file in `gnuRadio_env/grgym/scenarios`. You have to implement the `gnu_case` interface. Therefore, you have to include 

```
from grgym.envs.gnu_case import gnu_case
```
The interface expects you to implement the functions:
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
- `self.gnuradio.set_parameter('gr_var', value)`: You can set a variable of a GNU-Radio GUI block or a variable block via this method.

### Changing the configuration file
Via the configuration file `params/config.conf` you can configure the environment and your scenario model. For the generic part, you can set:
- `scenario`: The module and the class of your specific scenario environment
- `rpchost`: Server address of the GNU-Radio XMLRPC-Server
- `rpcport`: Port number of the GNU-Radio XMLRPC-Server
- `stepTime`: Duration of time the environment has to wait between execution of an action and the collection of the reward
- `simulate`: Enable or disable the execution of the `simulate` methode
- `simTime`: Duration of time the environment has to wait between changing the simulation and the collection of the observation

For our IEEE 802.11p scenario, you can configure:
- `simCount`: Number of steps with equal simulation (no change of simulation parameter within these number of steps)
- `simDistMin`: Minimum distance between sender and receiver in dB
- `simDistMax`: Maximum distance between sender and receiver in dB

## Writing your agent

To implement your own agent, you have to follow OpenAI gym implementation rules. First, you have to import gym
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

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* This is a student project of TU Berlin
* Thanks to our supervisor Dr. Anatolij Zubow
* and the complete TKN Group
