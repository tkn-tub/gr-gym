/* -*- c++ -*- */
/*
 * Copyright 2023 roesler.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_GNUGYM_CALCULATETXDURATION_H
#define INCLUDED_GNUGYM_CALCULATETXDURATION_H

#include <gnuradio/gnugym/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace gnugym {

    /*!
     * \brief <+description of block+>
     * \ingroup gnugym
     *
     */
    class GNUGYM_API calculateTxDuration : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<calculateTxDuration> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of gnugym::calculateTxDuration.
       *
       * To avoid accidental use of raw pointers, gnugym::calculateTxDuration's
       * constructor is in a private implementation
       * class. gnugym::calculateTxDuration::make is the public interface for
       * creating new instances.
       */
      static sptr make(float sample_rate,  bool debug = false);
    };

  } // namespace gnugym
} // namespace gr

#endif /* INCLUDED_GNUGYM_CALCULATETXDURATION_H */
