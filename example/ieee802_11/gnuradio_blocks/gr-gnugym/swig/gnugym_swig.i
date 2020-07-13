/* -*- c++ -*- */

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
