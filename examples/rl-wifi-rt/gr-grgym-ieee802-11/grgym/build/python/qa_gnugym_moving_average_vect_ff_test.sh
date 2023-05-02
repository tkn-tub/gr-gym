#!/usr/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir="/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python"
export GR_CONF_CONTROLPORT_ON=False
export PATH="/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/build/python":"$PATH"
export LD_LIBRARY_PATH="":$LD_LIBRARY_PATH
export PYTHONPATH=/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/build/test_modules:$PYTHONPATH
/usr/bin/python3 /home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/qa_gnugym_moving_average_vect_ff.py 
