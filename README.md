# Project Title

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

There are several parts, you have to install.
Please, first get and install OpenAI gym. Perhaps, you should do the installation in a new virtual python environment. You find OpenAI gym here: https://github.com/openai/gym
Next, you need an installation of GNU-Radio. For linux, you can use the official GNU-Radio packet repository. We are using GNU-Radio 3.7.11. Here, you find information for the installation of GNU-Radio: https://wiki.gnuradio.org/index.php/UbuntuInstall
If you want to use the IEEE 802.11p example, you have to install the GNU-Radio blocks of Sebastian Blosel. See his github repository for the code and more information: https://github.com/bastibl/gr-ieee802-11

Now, you have installed all required prequisites and you are ready to install our work. Therefore, please get our work:
```
git clone git@gitlab.tubit.tu-berlin.de:ali_alouane/GnuRadio_Gym.git
```

For the IEEE 802.11p Scenario controlling the modulation and the coding rate, you have to install our extension blocks. Therefore, please do the following steps
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

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
