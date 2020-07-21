/*
 * Copyright (C) 2016 Bastian Bloessl <bloessl@ccs-labs.org>
 * and 2020 Sascha Rösler, TU Berlin <s.roesler@campus.tu-berlin.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#ifndef INCLUDED_GNUGYM_PARSE_SEQNR_H
#define INCLUDED_GNUGYM_PARSE_SEQNR_H

#include <gnugym/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace gnugym {

class GNUGYM_API gnugym_parse_seqnr : virtual public block
{
public:

	typedef boost::shared_ptr<gnugym_parse_seqnr> sptr;
	static sptr make(bool log = false, bool debug = false);

};

} // namespace ieee802_11
} // namespace gr

#endif /* INCLUDED_GNUGYM_PARSE_SEQNR_H */
