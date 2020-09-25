#
# Copyright (C) 2013 Bastian Bloessl <bloessl@ccs-labs.org>
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
# Check if there is C++ code at all
########################################################################
if(NOT gnugym_sources)
    MESSAGE(STATUS "No C++ sources... skipping swig/")
    return()
endif(NOT gnugym_sources)

########################################################################
# Include swig generation macros
########################################################################
find_package(SWIG)
find_package(PythonLibs)
if(NOT SWIG_FOUND OR NOT PYTHONLIBS_FOUND)
    return()
endif()
include(GrSwig)
include(GrPython)

########################################################################
# Setup swig generation
########################################################################
set(GR_SWIG_INCLUDE_DIRS $<TARGET_PROPERTY:gnuradio::runtime_swig,INTERFACE_INCLUDE_DIRECTORIES>)
set(GR_SWIG_TARGET_DEPS gnuradio::runtime_swig)

set(GR_SWIG_LIBRARIES gnuradio-gnugym)

set(GR_SWIG_DOC_FILE ${CMAKE_CURRENT_BINARY_DIR}/gnugym_swig_doc.i)
set(GR_SWIG_DOC_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/../include)

GR_SWIG_MAKE(gnugym_swig gnugym_swig.i)

########################################################################
# Install the build swig module
########################################################################
GR_SWIG_INSTALL(TARGETS gnugym_swig DESTINATION ${GR_PYTHON_DIR}/gnugym)

########################################################################
# Install swig .i files for development
########################################################################
install(
    FILES
    gnugym_swig.i
    ${CMAKE_CURRENT_BINARY_DIR}/gnugym_swig_doc.i
    DESTINATION ${GR_INCLUDE_DIR}/gnugym/swig
)
