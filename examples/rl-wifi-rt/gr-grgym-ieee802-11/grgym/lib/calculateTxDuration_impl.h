/* -*- c++ -*- */
/*
 * Copyright 2023 roesler.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_GNUGYM_CALCULATETXDURATION_IMPL_H
#define INCLUDED_GNUGYM_CALCULATETXDURATION_IMPL_H

#include <gnuradio/gnugym/calculateTxDuration.h>

namespace gr {
  namespace gnugym {

    class calculateTxDuration_impl : public calculateTxDuration
    {
     private:
      float sample_rate;
      bool d_debug;

     public:
      calculateTxDuration_impl(float sample_rate, bool debug);
      ~calculateTxDuration_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace gnugym
} // namespace gr

#endif /* INCLUDED_GNUGYM_CALCULATETXDURATION_IMPL_H */
