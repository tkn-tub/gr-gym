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


#ifndef INCLUDED_GNUGYM_GNUGYM_RSSI_CB_H
#define INCLUDED_GNUGYM_GNUGYM_RSSI_CB_H

#include <gnuradio/gnugym/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace gnugym {

    /*!
     * \brief <+description of block+>
     * \ingroup gnugym
     *
     */
    class GNUGYM_API gnugym_rssi_cb : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<gnugym_rssi_cb> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of gnugym::gnugym_rssi_cb.
       *
       * To avoid accidental use of raw pointers, gnugym::gnugym_rssi_cb's
       * constructor is in a private implementation
       * class. gnugym::gnugym_rssi_cb::make is the public interface for
       * creating new instances.
       */
      static sptr make(double freq, double bw, bool log, bool debug);
    };

  } // namespace gnugym
} // namespace gr

#endif /* INCLUDED_GNUGYM_GNUGYM_RSSI_CB_H */

