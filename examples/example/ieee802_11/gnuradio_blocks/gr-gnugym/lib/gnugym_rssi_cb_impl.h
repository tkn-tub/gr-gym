/* -*- c++ -*- */
/* 
 * Copyright 2020 Sascha Rösler TU Berlin, 2016 Bastian Bloessl <bloessl@ccs-labs.org>
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

#ifndef INCLUDED_GNUGYM_GNUGYM_RSSI_CB_IMPL_H
#define INCLUDED_GNUGYM_GNUGYM_RSSI_CB_IMPL_H

#include <gnugym/gnugym_rssi_cb.h>
#include "equalizer/base.h"


namespace gr {
  namespace gnugym {

    class gnugym_rssi_cb_impl : public gnugym_rssi_cb
    {
     private:
      // Nothing to declare in this block.

     public:
      gnugym_rssi_cb_impl(double freq, double bw, bool log, bool debug);
      ~gnugym_rssi_cb_impl();
      
	  void set_bandwidth(double bw);
	  void set_frequency(double freq);
	
      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

private:


	bool parse_signal(uint8_t *signal);
	bool decode_signal_field(uint8_t *rx_bits);
	void deinterleave(uint8_t *rx_bits);

	equalizer::base *d_equalizer;
	gr::thread::mutex d_mutex;
	std::vector<gr::tag_t> tags;
	bool d_debug;
	bool d_log;
	int  d_current_symbol;
	//viterbi_decoder d_decoder;

	// freq offset
	double d_freq;  // Hz
	double d_freq_offset_from_synclong;  // Hz, estimation from "sync_long" block
	double d_bw;  // Hz
	double d_er;
	double d_epsilon0;
	gr_complex d_prev_pilots[4];

	int  d_frame_bytes;
	int  d_frame_symbols;
	int  d_frame_encoding;

	uint8_t d_deinterleaved[48];
	gr_complex symbols[48];

	boost::shared_ptr<gr::digital::constellation> d_frame_mod;
	constellation_bpsk::sptr d_bpsk;
	constellation_qpsk::sptr d_qpsk;
	constellation_16qam::sptr d_16qam;
	constellation_64qam::sptr d_64qam;

	static const int interleaver_pattern[48];
    };

  } // namespace gnugym
} // namespace gr

#endif /* INCLUDED_GNUGYM_GNUGYM_RSSI_CB_IMPL_H */

