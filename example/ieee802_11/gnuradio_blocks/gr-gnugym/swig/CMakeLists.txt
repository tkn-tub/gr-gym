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
# Include swig generation macros
########################################################################
find_package(SWIG)
find_package(PythonLibs 2)
if(NOT SWIG_FOUND OR NOT PYTHONLIBS_FOUND)
    message(FATAL_ERROR "Python or Swig not found (or version not supported).")
    return()
endif()
include(GrSwig)
include(GrPython)

set(GR_SWIG_INCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/
    ${CMAKE_CURRENT_BINARY_DIR}/../include/
)

########################################################################
# Setup swig generation
########################################################################
foreach(incdir ${GNURADIO_RUNTIME_INCLUDE_DIRS})
    list(APPEND GR_SWIG_INCLUDE_DIRS ${incdir}/gnuradio/swig)
endforeach(incdir)

set(GR_SWIG_LIBRARIES gnuradio-gnugym)
set(GR_SWIG_DOC_FILE ${CMAKE_CURRENT_BINARY_DIR}/gnugym_swig_doc.i)
set(GR_SWIG_DOC_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/gnugym/
    ${CMAKE_CURRENT_BINARY_DIR}/../include/gnugym/
)

set(GR_SWIG_TARGET_DEPS gnugym_generated_includes)

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
