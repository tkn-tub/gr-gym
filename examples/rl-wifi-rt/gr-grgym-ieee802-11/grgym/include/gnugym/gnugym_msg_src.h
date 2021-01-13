/* -*- c++ -*- */
/*
 + (C) A. Zubow, TU Berlin. <zubow@tkn.tu-berlin.de>
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


#ifndef INCLUDED_GNUGYM_MSG_SRC_H
#define INCLUDED_GNUGYM_MSG_SRC_H

#include <gnugym/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace gnugym {

    /*!
     * \brief <+description of block+>
     * \ingroup gnugym
     *
     */
    class GNUGYM_API gnugym_msg_src : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<gnugym_msg_src> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of gnugym::gnugym_msg_src.
       *
       * To avoid accidental use of raw pointers, gnugym::gnugym_msg_src's
       * constructor is in a private implementation
       * class. gnugym::gnugym_msg_src::make is the public interface for
       * creating new instances.
       */
      static sptr make(pmt::pmt_t msg, int trigger);

    /*!
     * Reset the message being sent.
     * \param msg The message to send as a PMT.
     */
    virtual void set_msg(pmt::pmt_t msg) = 0;

    /*!
     * Get the value of the message being sent.
     */
    virtual pmt::pmt_t msg() const = 0;

    /*!
     * Reset the the trigger
     */
    virtual void set_trigger(int trigger) = 0;

    /*!
     * Get the
     */
    virtual int trigger() const = 0;
    };

  } // namespace gnugym
} // namespace gr

#endif /* INCLUDED_GNUGYM_MSG_SRC_H */

