# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT gnugym_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT gnugym_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND gnugym_python_files
    gnugym_moving_average_vect_ff_python.cc
    gnugym_parse_seqnr_python.cc
    gnugym_rssi_cb_python.cc
    gnugym_snr_cb_python.cc
    gnugym_snrdebug_ff_python.cc
    calculateTxDuration_python.cc python_bindings.cc)

GR_PYBIND_MAKE_OOT(gnugym
   ../..
   gr::gnugym
   "${gnugym_python_files}")

# copy in bindings .so file for use in QA test module
add_custom_target(
  copy_bindings_for_tests ALL
  COMMAND
    ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_BINARY_DIR}/*.so"
    ${CMAKE_BINARY_DIR}/test_modules/gnuradio/gnugym/
  DEPENDS gnugym_python)

install(TARGETS gnugym_python DESTINATION ${GR_PYTHON_DIR}/gnuradio/gnugym COMPONENT pythonapi)
