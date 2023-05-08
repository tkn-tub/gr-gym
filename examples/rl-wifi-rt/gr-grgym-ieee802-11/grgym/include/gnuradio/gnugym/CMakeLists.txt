# Copyright 2011,2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Install public header files
########################################################################
#install(FILES
#    api.h
#    constellations.h
#    gnugym_rssi_cb.h
#
#    zwei_test.h
#    calculateTxDuration.h DESTINATION include/gnugym
#)

#
#  Copyright (C) 2013, 2016 Bastian Bloessl <bloessl@ccs-labs.org>
#  Copyright (C) 2020 Sascha Rösler <s.roesler@campus.tu-berlin.de>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


########################################################################
# Install public header files
########################################################################

list(APPEND include_sources
#    ${generated_includes}
    api.h
    constellations.h
    gnugym_rssi_cb.h
    gnugym_snr_cb.h
    gnugym_snrdebug_ff.h
    gnugym_moving_average_vect_ff.h
    gnugym_parse_seqnr.h
    calculateTxDuration.h
)

install(
	FILES ${include_sources}
	DESTINATION ${GR_INCLUDE_DIR}
	COMPONENT "gnugym_devel"
)
