/*
 * Copyright (C) 2016 Bastian Bloessl <bloessl@ccs-labs.org>
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

#ifndef INCLUDED_GNUGYM_CONSTELLATIONS_H
#define INCLUDED_GNUGYM_CONSTELLATIONS_H

#include <gnuradio/gnugym/api.h>
#include <gnuradio/digital/constellation.h>

namespace gr {
namespace gnugym {

class GNUGYM_API constellation_bpsk : virtual public digital::constellation
{
public:
	typedef std::shared_ptr<gr::gnugym::constellation_bpsk> sptr;
	static sptr make();

protected:
	constellation_bpsk();
};

class GNUGYM_API constellation_qpsk : virtual public digital::constellation
{
public:
	typedef std::shared_ptr<gr::gnugym::constellation_qpsk> sptr;
	static sptr make();

protected:
	constellation_qpsk();
};

class GNUGYM_API constellation_16qam : virtual public digital::constellation
{
public:
	typedef std::shared_ptr<gr::gnugym::constellation_16qam> sptr;
	static sptr make();

protected:
	constellation_16qam();
};

class GNUGYM_API constellation_64qam : virtual public digital::constellation
{
public:
	typedef std::shared_ptr<gr::gnugym::constellation_64qam> sptr;
	static sptr make();

protected:
	constellation_64qam();
};

} // namespace GNUGYM
} // namespace gr

#endif /* INCLUDED_GNUGYM_CONSTELLATIONS_H */

