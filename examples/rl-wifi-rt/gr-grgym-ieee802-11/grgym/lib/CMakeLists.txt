#
# Copyright (C) 2013, 2016 Bastian Bloessl <bloessl@ccs-labs.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX
check_include_file("xmmintrin.h" SSE2_SUPPORTED)

if(SSE2_SUPPORTED)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -msse2")
    add_definitions(-DIEEE80211_MSSE2)
endif(SSE2_SUPPORTED)

########################################################################
# Setup library
########################################################################
list(APPEND gnugym_sources
#    ${generated_sources}
    constellations_impl.cc
    gnugym_rssi_cb_impl.cc
    gnugym_snr_cb_impl.cc
    equalizer/base.cc
    equalizer/comb.cc
    equalizer/ls.cc
    equalizer/lms.cc
    equalizer/sta.cc
    gnugym_snrdebug_ff_impl.cc
    gnugym_moving_average_vect_ff_impl.cc
    gnugym_parse_seqnr_impl.cc
    calculateTxDuration_impl.cc
)

set(gnugym_sources "${gnugym_sources}" PARENT_SCOPE)
if(NOT gnugym_sources)
    MESSAGE(STATUS "No C++ sources... skipping lib/")
    return()
endif(NOT gnugym_sources)

add_library(gnuradio-gnugym SHARED ${gnugym_sources})
target_link_libraries(gnuradio-gnugym
        gnuradio::gnuradio-runtime
        gnuradio::gnuradio-filter
        gnuradio::gnuradio-blocks
        gnuradio::gnuradio-analog
        gnuradio::gnuradio-fft
        gnuradio::gnuradio-digital)
target_include_directories(gnuradio-gnugym
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
    PUBLIC $<INSTALL_INTERFACE:include>
  )
set_target_properties(gnuradio-gnugym PROPERTIES DEFINE_SYMBOL "gnuradio_gnugym_EXPORTS")

if(APPLE)
    set_target_properties(gnuradio-gnugym PROPERTIES
        INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib"
    )
endif(APPLE)

########################################################################
# Install built library files
########################################################################
include(GrMiscUtils)
GR_LIBRARY_FOO(gnuradio-gnugym)

########################################################################
# Print summary
########################################################################
message(STATUS "Using install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "Building for version: ${VERSION} / ${LIBVER}")

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

# If your unit tests require special include paths, add them here
#include_directories()
# List all files that contain Boost.UTF unit tests here
list(APPEND test_gnugym_sources
)
# Anything we need to link to for the unit tests go here
list(APPEND GR_TEST_TARGET_DEPS gnuradio-gnugym)

if(NOT test_gnugym_sources)
    MESSAGE(STATUS "No C++ unit tests... skipping")
    return()
endif(NOT test_gnugym_sources)

foreach(qa_file ${test_gnugym_sources})
    GR_ADD_CPP_TEST("gnugym_${qa_file}"
        ${CMAKE_CURRENT_SOURCE_DIR}/${qa_file}
    )
endforeach(qa_file)
