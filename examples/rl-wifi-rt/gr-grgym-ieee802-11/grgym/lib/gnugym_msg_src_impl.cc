/* -*- c++ -*- */
/*
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
#include "gnugym_msg_src_impl.h"
#define dout d_debug && std::cout

namespace gr {
  namespace gnugym {

    gnugym_msg_src::sptr gnugym_msg_src::make(pmt::pmt_t msg, int trigger)
    {
        return gnuradio::get_initial_sptr(new gnugym_msg_src_impl(msg, trigger));
    }

    gnugym_msg_src_impl::gnugym_msg_src_impl(pmt::pmt_t msg, int trigger)
        : block("gnugym_msg_src", io_signature::make(0, 0, 0), io_signature::make(0, 0, 0)),
          //d_finished(false),
          d_trigger(trigger),
          d_msg(msg),
          d_port(pmt::mp("strobe"))
    {
        message_port_register_out(d_port);

        message_port_register_in(pmt::mp("set_msg"));
        set_msg_handler(pmt::mp("set_msg"),
                        boost::bind(&gnugym_msg_src_impl::set_msg, this, _1));
    }

    gnugym_msg_src_impl::~gnugym_msg_src_impl() {}

    void
    gnugym_msg_src_impl::set_trigger(int trigger) {
        d_trigger = trigger;
	std::cout << "Message send" << std::endl;
        message_port_pub(d_port, d_msg);
    }


  } /* namespace gnugym */
} /* namespace gr */

