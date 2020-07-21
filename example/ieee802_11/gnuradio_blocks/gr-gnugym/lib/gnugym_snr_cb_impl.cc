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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <gnugym/constellations.h>
#include "gnugym_snr_cb_impl.h"
#include "equalizer/base.h"
#include "equalizer/comb.h"
#include "equalizer/lms.h"
#include "equalizer/ls.h"
#include "equalizer/sta.h"
#define dout d_debug && std::cout

namespace gr {
  namespace gnugym {

    gnugym_snr_cb::sptr
    gnugym_snr_cb::make(EqualizerSNR algo, double freq, double bw, bool log, bool debug)
    {
      return gnuradio::get_initial_sptr
        (new gnugym_snr_cb_impl(algo,  freq, bw, log, debug));
    }

    /*
     * The private constructor
     */
    gnugym_snr_cb_impl::gnugym_snr_cb_impl(EqualizerSNR algo, double freq, double bw, bool log, bool debug)
      : gr::block("gnugym_snr_cb",
			gr::io_signature::make(1, -1, 64 * sizeof(gr_complex)),
			gr::io_signature::make(1, -1, 64 * sizeof(float))),
	d_current_symbol(0), d_log(log), d_debug(debug), d_equalizer(NULL),
	d_freq(freq), d_bw(bw), d_frame_bytes(0), d_frame_symbols(0),
	d_freq_offset_from_synclong(0.0) {

	    d_bpsk = constellation_bpsk::make();
	    d_qpsk = constellation_qpsk::make();
	    d_16qam = constellation_16qam::make();
	    d_64qam = constellation_64qam::make();

	    d_frame_mod = d_bpsk;

	    set_tag_propagation_policy(block::TPP_DONT);
	    set_algorithm(algo);
	}

    /*
     * Our virtual destructor.
     */
    gnugym_snr_cb_impl::~gnugym_snr_cb_impl()
    {
    }

    void
    gnugym_snr_cb_impl::set_algorithm(EqualizerSNR algo) {
	    gr::thread::scoped_lock lock(d_mutex);
	    delete d_equalizer;

	    switch(algo) {

	    case COMB_SNR:
		    dout << "Comb" << std::endl;
		    d_equalizer = new equalizer::comb();
		    break;
	    case LS_SNR:
		    dout << "LS" << std::endl;
		    d_equalizer = new equalizer::ls();
		    break;
	    case LMS_SNR:
		    dout << "LMS" << std::endl;
		    d_equalizer = new equalizer::lms();
		    break;
	    case STA_SNR:
		    dout << "STA" << std::endl;
		    d_equalizer = new equalizer::sta();
		    break;
	    default:
		    throw std::runtime_error("Algorithm not implemented");
	    }
    }

    void
    gnugym_snr_cb_impl::set_bandwidth(double bw) {
	    gr::thread::scoped_lock lock(d_mutex);
	    d_bw = bw;
    }

    void
    gnugym_snr_cb_impl::set_frequency(double freq) {
	    gr::thread::scoped_lock lock(d_mutex);
	    d_freq = freq;
    }

    void
    gnugym_snr_cb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    gnugym_snr_cb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      gr::thread::scoped_lock lock(d_mutex);

	    const gr_complex *in = (const gr_complex *) input_items[0];
	    float *out = (float *) output_items[0];

	    int i = 0;
	    int o = 0;
	    uint8_t bits[64];
	    //int snr_vect[48];
	    gr_complex current_symbol[64];

	    dout << "FRAME EQUALIZER: input " << ninput_items[0] << "  output " << noutput_items << std::endl;

	    while((i < ninput_items[0]) && (o < noutput_items)) {

		    get_tags_in_window(tags, 0, i, i + 1, pmt::string_to_symbol("wifi_start"));

		    // new frame
		    if(tags.size()) {
			    d_current_symbol = 0;
			    d_frame_symbols = 0;
			    d_frame_mod = d_bpsk;

			    d_freq_offset_from_synclong = pmt::to_double(tags.front().value) * d_bw / (2 * M_PI);
			    d_epsilon0 = pmt::to_double(tags.front().value) * d_bw / (2 * M_PI * d_freq);
			    d_er = 0;

			    dout << "epsilon: " << d_epsilon0 << std::endl;
		    }

		    // not interesting -> skip
		    if(d_current_symbol > (d_frame_symbols + 2)) {
			    i++;
			    continue;
		    }

		    std::memcpy(current_symbol, in + i*64, 64*sizeof(gr_complex));

		    // compensate sampling offset
		    for(int i = 0; i < 64; i++) {
			    current_symbol[i] *= exp(gr_complex(0, 2*M_PI*d_current_symbol*80*(d_epsilon0 + d_er)*(i-32)/64));
		    }

		    gr_complex p = equalizer::base::POLARITY[(d_current_symbol - 2) % 127];
		    gr_complex sum =
			    (current_symbol[11] *  p) +
			    (current_symbol[25] *  p) +
			    (current_symbol[39] *  p) +
			    (current_symbol[53] * -p);

		    double beta;
		    if(d_current_symbol < 2) {
			    beta = arg(
					    current_symbol[11] -
					    current_symbol[25] +
					    current_symbol[39] +
					    current_symbol[53]);

		    } else {
			    beta = arg(
					    (current_symbol[11] *  p) +
					    (current_symbol[39] *  p) +
					    (current_symbol[25] *  p) +
					    (current_symbol[53] * -p));
		    }

		    double er = arg(
				    (conj(d_prev_pilots[0]) * current_symbol[11] *  p) +
				    (conj(d_prev_pilots[1]) * current_symbol[25] *  p) +
				    (conj(d_prev_pilots[2]) * current_symbol[39] *  p) +
				    (conj(d_prev_pilots[3]) * current_symbol[53] * -p));

		    er *= d_bw / (2 * M_PI * d_freq * 80);

		    d_prev_pilots[0] = current_symbol[11] *  p;
		    d_prev_pilots[1] = current_symbol[25] *  p;
		    d_prev_pilots[2] = current_symbol[39] *  p;
		    d_prev_pilots[3] = current_symbol[53] * -p;

		    // compensate residual frequency offset
		    for(int i = 0; i < 64; i++) {
			    current_symbol[i] *= exp(gr_complex(0, -beta));
		    }

		    // calculate SNR from first two samples
		    if(d_current_symbol < 2)
		        d_equalizer->equalize(current_symbol, d_current_symbol,
				        symbols, bits, d_frame_mod, out + o * 64 * sizeof(float), true);
	        if(d_current_symbol == 1){
	            o ++;
	            }
		    i++;
		    d_current_symbol++;
	    }

	    consume(0, i);
	    return o;
    }

  } /* namespace gnugym */
} /* namespace gr */

