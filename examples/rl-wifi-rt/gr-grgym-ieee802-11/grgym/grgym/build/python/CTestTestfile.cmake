# CMake generated Testfile for 
# Source directory: /home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python
# Build directory: /home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/build/python
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(qa_gnugym_moving_average_vect_ff "/usr/bin/sh" "qa_gnugym_moving_average_vect_ff_test.sh")
set_tests_properties(qa_gnugym_moving_average_vect_ff PROPERTIES  _BACKTRACE_TRIPLES "/usr/lib/x86_64-linux-gnu/cmake/gnuradio/GrTest.cmake;116;add_test;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;42;GR_ADD_TEST;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;0;")
add_test(qa_gnugym_parse_seqnr "/usr/bin/sh" "qa_gnugym_parse_seqnr_test.sh")
set_tests_properties(qa_gnugym_parse_seqnr PROPERTIES  _BACKTRACE_TRIPLES "/usr/lib/x86_64-linux-gnu/cmake/gnuradio/GrTest.cmake;116;add_test;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;43;GR_ADD_TEST;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;0;")
add_test(qa_gnugym_rssi_cb "/usr/bin/sh" "qa_gnugym_rssi_cb_test.sh")
set_tests_properties(qa_gnugym_rssi_cb PROPERTIES  _BACKTRACE_TRIPLES "/usr/lib/x86_64-linux-gnu/cmake/gnuradio/GrTest.cmake;116;add_test;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;44;GR_ADD_TEST;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;0;")
add_test(qa_gnugym_snr_cb "/usr/bin/sh" "qa_gnugym_snr_cb_test.sh")
set_tests_properties(qa_gnugym_snr_cb PROPERTIES  _BACKTRACE_TRIPLES "/usr/lib/x86_64-linux-gnu/cmake/gnuradio/GrTest.cmake;116;add_test;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;45;GR_ADD_TEST;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;0;")
add_test(qa_gnugym_snrdebug_ff "/usr/bin/sh" "qa_gnugym_snrdebug_ff_test.sh")
set_tests_properties(qa_gnugym_snrdebug_ff PROPERTIES  _BACKTRACE_TRIPLES "/usr/lib/x86_64-linux-gnu/cmake/gnuradio/GrTest.cmake;116;add_test;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;46;GR_ADD_TEST;/home/roesler/project_openai_gnuradio/GnuRadio_Gym/example/ieee802_11/gnuradio_blocks/grgym/python/CMakeLists.txt;0;")
subdirs("bindings")
