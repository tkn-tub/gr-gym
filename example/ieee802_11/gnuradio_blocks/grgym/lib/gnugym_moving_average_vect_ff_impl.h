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

#ifndef INCLUDED_GNUGYM_GNUGYM_MOVING_AVERAGE_VECT_FF_IMPL_H
#define INCLUDED_GNUGYM_GNUGYM_MOVING_AVERAGE_VECT_FF_IMPL_H

#include <gnugym/gnugym_moving_average_vect_ff.h>
#include "equalizer/base.h"


namespace gr {
  namespace gnugym {

    class gnugym_moving_average_vect_ff_impl : public gnugym_moving_average_vect_ff
    {
     private:
      float* d_buffer;
      int d_vlen;

     public:
      gnugym_moving_average_vect_ff_impl(int vlen);
      ~gnugym_moving_average_vect_ff_impl();
      
      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);
      std::vector<double> getLastOutput();

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace gnugym
} // namespace gr

#endif /* INCLUDED_GNUGYM_GNUGYM_MOVING_AVERAGE_VECT_FF_IMPL_H */

