/* -*- c++ -*- */
/*
 * Copyright 2023 roesler.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/io_signature.h>
#include "calculateTxDuration_impl.h"

namespace gr {
  namespace gnugym {

    using input_type = gr_complex;
    using output_type = float;
    calculateTxDuration::sptr
    calculateTxDuration::make(float sample_rate, bool debug)
    {
      return gnuradio::make_block_sptr<calculateTxDuration_impl>(
        sample_rate, debug);
    }


    /*
     * The private constructor
     */
    calculateTxDuration_impl::calculateTxDuration_impl(float sample_rate, bool debug)
      : gr::block("calculateTxDuration",
              gr::io_signature::make(1 /* min inputs */, 1 /* max inputs */, sizeof(input_type)),
              gr::io_signature::make(1 /* min outputs */, 1 /*max outputs */, sizeof(output_type))),
              sample_rate(sample_rate),
              d_debug(debug)
    {}

    /*
     * Our virtual destructor.
     */
    calculateTxDuration_impl::~calculateTxDuration_impl()
    {
    }

    void
    calculateTxDuration_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    calculateTxDuration_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      auto in = static_cast<const input_type*>(input_items[0]);
      auto out = static_cast<output_type*>(output_items[0]);
      
      noutput_items = 0;
      
      if(ninput_items[0] > 0){
        if (d_debug){
            std::cout << "TX Duration get " << (int) ninput_items[0] << "samples" << std::endl;
        }
        
        std::vector<tag_t> tags;
      
        get_tags_in_range(
        tags, 0, nitems_read(0), nitems_read(0) + ninput_items[0], pmt::mp("seqnr"));

        int seqnr = -1;
        
        if (tags.size() == 1) {
            seqnr = (int)pmt::to_long(tags[0].value);
            
            if (d_debug){
                std::cout << "TX Duration get packet" << seqnr << std::endl;
            }
            
        }
        
        float txduration = ninput_items[0] * 1 / sample_rate;
        if (d_debug){
            std::cout << "TX Duration " << txduration << std::endl;
        }
        
        out[0] = (float) seqnr;
        out[1] = txduration;
        noutput_items = 2;
      }
      
      //consume all
      consume_each (ninput_items[0]);
      
      return noutput_items;
    }

  } /* namespace gnugym */
} /* namespace gr */
