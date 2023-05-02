/* -*- c++ -*- */
/* 
 * Copyright (C) 2016 Bastian Bloessl <bloessl@ccs-labs.org>
 * and 2020 Sascha Rösler, TU Berlin <s.roesler@campus.tu-berlin.de>
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */


#ifndef INCLUDED_GNUGYM_GNUGYM_SNR_CB_H
#define INCLUDED_GNUGYM_GNUGYM_SNR_CB_H

#include <gnugym/api.h>
#include <gnuradio/block.h>

enum EqualizerSNR {
	LS_SNR   = 0,
	LMS_SNR  = 1,
	COMB_SNR = 2,
	STA_SNR  = 3,
};

namespace gr {
  namespace gnugym {

    /*!
     * \brief <+description of block+>
     * \ingroup gnugym
     *
     */
    class GNUGYM_API gnugym_snr_cb : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<gnugym_snr_cb> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of gnugym::gnugym_snr_cb.
       *
       * To avoid accidental use of raw pointers, gnugym::gnugym_snr_cb's
       * constructor is in a private implementation
       * class. gnugym::gnugym_snr_cb::make is the public interface for
       * creating new instances.
       */
      static sptr make(EqualizerSNR algo, double freq, double bw, bool log, bool debug);
    };

  } // namespace gnugym
} // namespace gr

#endif /* INCLUDED_GNUGYM_GNUGYM_SNR_CB_H */

