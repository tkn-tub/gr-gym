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

#include "ls.h"
#include <cstring>
#include <iostream>

using namespace gr::gnugym::equalizer;

void ls::equalize(gr_complex *in, int n, gr_complex *symbols, uint8_t *bits, std::shared_ptr<gr::digital::constellation> mod, float* snrVect, bool onlyRssi) {

	if(n == 0) {
		std::memcpy(d_H, in, 64 * sizeof(gr_complex));

	} else if(n == 1) {
		double signal = 0;
		double mySignal = 0;
		double noise = 0;
		double myNoise = 0;
		for(int i = 0; i < 64; i++) {
			if((i == 32) || (i < 6) || ( i > 58)) {
				continue;
			}
			mySignal = std::pow(std::abs(d_H[i] - in[i]), 2);
			myNoise = std::pow(std::abs(d_H[i] + in[i]), 2);
			signal += mySignal;
			noise += myNoise;
			d_H[i] += in[i];
			d_H[i] /= LONG[i] * gr_complex(2, 0);
			
			snrVect[i] = 10 * std::log10(mySignal / myNoise / 2);
			//std::cout << "signal: " << mySignal << ", noise: " << myNoise << ", SNR: " << snrVect[i] << "\n";
		}

		d_snr = 10 * std::log10(signal / noise / 2);

	} else if(!onlyRssi) {

		int c = 0;
		for(int i = 0; i < 64; i++) {
			if( (i == 11) || (i == 25) || (i == 32) || (i == 39) || (i == 53) || (i < 6) || ( i > 58)) {
				continue;
			} else {
				symbols[c] = in[i] / d_H[i];
				bits[c] = mod->decision_maker(&symbols[c]);
				c++;
			}
		}
	}
}

double ls::get_snr() {
	return d_snr;
}
