/* -*- c++ -*- */
/*
 * Copyright 2013, 2019 Bastian Bloessl <mail@bastibl.net>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#define GNUGYM_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "gnugym_swig_doc.i"

%{
#include "gnugym/gnugym_rssi_cb.h"
#include "gnugym/gnugym_snr_cb.h"
#include "gnugym/gnugym_snrdebug_cb.h"
#include "gnugym/gnugym_moving_average_vect_ff.h"
#include "gnugym/gnugym_parse_seqnr.h"
%}


%include "gnugym/gnugym_rssi_cb.h"
%include "gnugym/gnugym_snr_cb.h"
%include "gnugym/gnugym_snrdebug_cb.h"
%include "gnugym/gnugym_moving_average_vect_ff.h"
%include "gnugym/gnugym_parse_seqnr.h"
GR_SWIG_BLOCK_MAGIC2(gnugym, gnugym_rssi_cb);
GR_SWIG_BLOCK_MAGIC2(gnugym, gnugym_snr_cb);
GR_SWIG_BLOCK_MAGIC2(gnugym, gnugym_snrdebug_ff);
GR_SWIG_BLOCK_MAGIC2(gnugym, gnugym_moving_average_vect_ff);
GR_SWIG_BLOCK_MAGIC2(gnugym, gnugym_parse_seqnr);
