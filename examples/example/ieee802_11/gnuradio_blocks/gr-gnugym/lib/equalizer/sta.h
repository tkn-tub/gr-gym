/*
 * Copyright (C) 2015 Bastian Bloessl <bloessl@ccs-labs.org>
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

#ifndef INCLUDED_GNUGYM_EQUALIZER_STA_H
#define INCLUDED_GNUGYM_EQUALIZER_STA_H

#include "base.h"
#include <vector>

namespace gr {
namespace gnugym {
namespace equalizer {

class sta: public base {
public:
	virtual void equalize(gr_complex *in, int n, gr_complex *symbols, uint8_t *bits, boost::shared_ptr<gr::digital::constellation> mod, float* snrVect, bool onlyRssi);
	double get_snr();

private:
	gr_complex d_H[64];
	double d_snr;

	const double alpha = 0.5;
	const int beta = 2;
};

} /* namespace channel_estimation */
} /* namespace gnugym */
} /* namespace gr */

#endif /* INCLUDED_GNUGYM_EQUALIZER_STA_H */
