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

#ifndef INCLUDED_GNUGYM_MSG_SRC_IMPL_H
#define INCLUDED_GNUGYM_MSG_SRC_IMPL_H

#include <gnugym/gnugym_msg_src.h>
#include "equalizer/base.h"


namespace gr {
  namespace gnugym {

    class gnugym_msg_src_impl : public gnugym_msg_src
    {
     private:
	    pmt::pmt_t d_msg;
        const pmt::pmt_t d_port;
	    int d_trigger;

     public:
      gnugym_msg_src_impl(pmt::pmt_t msg, int trigger);
      ~gnugym_msg_src_impl();

        void set_msg(pmt::pmt_t msg) { d_msg = msg; }
        pmt::pmt_t msg() const { return d_msg; }
        int trigger() const { return d_trigger; }

    };

  } // namespace gnugym
} // namespace gr

#endif /* INCLUDED_GNUGYM_MSG_SRC_IMPL_H */

