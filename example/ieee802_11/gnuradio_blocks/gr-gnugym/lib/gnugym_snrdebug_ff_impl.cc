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
#include "gnugym_snrdebug_ff_impl.h"
#define dout d_debug && std::cout

namespace gr {
  namespace gnugym {

    gnugym_snrdebug_ff_impl::sptr
    gnugym_snrdebug_ff::make()
    {
      return gnuradio::get_initial_sptr
        (new gnugym_snrdebug_ff_impl());
    }

    /*
     * The private constructor
     */
    gnugym_snrdebug_ff_impl::gnugym_snrdebug_ff_impl()
      : gr::block("gnugym_snrdebug",
			gr::io_signature::make(1, 1, 64 * sizeof(float)),
			//gr::io_signature::make(0, 0, 0))){
			gr::io_signature::make(1, 1, 64 * sizeof(float))){
	    set_tag_propagation_policy(block::TPP_DONT);
	}

    /*
     * Our virtual destructor.
     */
    gnugym_snrdebug_ff_impl::~gnugym_snrdebug_ff_impl()
    {
    }
    
    void
    gnugym_snrdebug_ff_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    gnugym_snrdebug_ff_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
	    const float *in = (const float *) input_items[0];
	    float *out = (float *) output_items[0];

	    int i = 0;
	    int o = 0;

        std::cout << "[";
	    while((i < ninput_items[0]) ) {
            for(int j = 0;j < 64;j ++){
                std::cout << in[j] <<",";        
            }
		    i++;
	    }
	    std::cout << "]";

	    consume(0, i);
	    return o;
    }

  } /* namespace gnugym */
} /* namespace gr */

