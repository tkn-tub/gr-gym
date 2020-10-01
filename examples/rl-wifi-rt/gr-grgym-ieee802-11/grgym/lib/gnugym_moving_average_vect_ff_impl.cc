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

#include <gnugym/constellations.h>
#include "gnugym_moving_average_vect_ff_impl.h"
#define dout d_debug && std::cout

namespace gr {
  namespace gnugym {

    gnugym_moving_average_vect_ff_impl::sptr
    gnugym_moving_average_vect_ff::make(int vlen, int buffer)
    {
      return gnuradio::get_initial_sptr
        (new gnugym_moving_average_vect_ff_impl(vlen));
    }

    /*
     * The private constructor
     */
    gnugym_moving_average_vect_ff_impl::gnugym_moving_average_vect_ff_impl(int vlen)
      : gr::block("gnugym_moving_average_vect",
			gr::io_signature::make(1, 1, vlen * sizeof(float)),
			gr::io_signature::make(1, 1, vlen * sizeof(float))),
			d_vlen(vlen){
	    set_tag_propagation_policy(block::TPP_DONT);
	    d_buffer = new float[vlen];
	    for(int j = 0; j < (vlen); j ++)
	        d_buffer[j] = 0.0;
	}

    /*
     * Our virtual destructor.
     */
    gnugym_moving_average_vect_ff_impl::~gnugym_moving_average_vect_ff_impl()
    {
        delete d_buffer;
    }
    
    void
    gnugym_moving_average_vect_ff_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    gnugym_moving_average_vect_ff_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
	    const float *in = (const float *) input_items[0];
	    float *out = (float *) output_items[0];

	    int i = 0;
	    int o = 0;
	    
        // IIR over SNR data
	    while((i < ninput_items[0]) ) {
	        const float *in = (const float *) input_items[i];
            for(int j = 0;j < d_vlen; j ++){
                d_buffer[j] = 0.5 * in[j] + 0.5 * d_buffer [j];
                (out + o * d_vlen* sizeof(float))[j] = d_buffer[j];
            }
		    i++;
		    o ++;
	    }

	    consume(0, i);
	    return o;
    }
    std::vector<double> gnugym_moving_average_vect_ff_impl::getLastOutput(void){
        std::vector<double> v= std::vector<double>();
        for(int i = 0; i < d_vlen; i ++)
            v.push_back(d_buffer[i]);
        return v;
    }

  } /* namespace gnugym */
} /* namespace gr */

