/*
 * Copyright (C) 2013, 2016 Bastian Bloessl <bloessl@ccs-labs.org>
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
#include <gnugym/gnugym_parse_seqnr.h>

#include <gnuradio/io_signature.h>
#include <gnuradio/block_detail.h>
#include <string>

using namespace gr::gnugym;

struct mac_header {
	//protocol version, type, subtype, to_ds, from_ds, ...
	uint16_t frame_control;
	uint16_t duration;
	uint8_t addr1[6];
	uint8_t addr2[6];
	uint8_t addr3[6];
	uint16_t seq_nr;
}__attribute__((packed));

class gnugym_parse_seqnr_impl : public gnugym_parse_seqnr {

public:

gnugym_parse_seqnr_impl(bool log, bool debug) :
		block("gnugym_parse_seqnr",
				gr::io_signature::make(0, 0, 0),
				gr::io_signature::make(2, 2, sizeof(int))),
		d_log(log), d_last_seq_no(-1),
		d_missing_seq_no(0),
		d_debug(debug) {

	message_port_register_in(pmt::mp("in"));
}

~gnugym_parse_seqnr_impl() {

}


int general_work(int noutput, gr_vector_int& ninput_items,
			gr_vector_const_void_star& input_items,
			gr_vector_void_star& output_items ) {

	int *out1 = (int*)output_items[0];
	int *out2 = (int*)output_items[1];
	
	pmt::pmt_t msg(delete_head_nowait(pmt::intern("in")));

	if(!msg.get()) {
		return 0;
	}
	
	if(pmt::is_eof_object(msg)) {
		detail().get()->set_done(true);
		return 0;
	} else if(pmt::is_symbol(msg)) {
		return 0;
	}

	msg = pmt::cdr(msg);

	int data_len = pmt::blob_length(msg);
	mac_header *h = (mac_header*)pmt::blob_data(msg);

	if(data_len < 20) {
		return 0;
	}
	
	// Extract sequence number and missing sequence numbers
	int seqnr = int(h->seq_nr >> 4);
	d_missing_seq_no += seqnr - d_last_seq_no -1;
	d_last_seq_no = seqnr;
	
	out1[0] = seqnr;
	out2[0] = d_missing_seq_no;
	
	return 1;
}

private:
	bool d_log;
	bool d_debug;
	int d_last_seq_no;
	int d_missing_seq_no;
};

gnugym_parse_seqnr::sptr
gnugym_parse_seqnr::make(bool log, bool debug) {
	return gnuradio::get_initial_sptr(new gnugym_parse_seqnr_impl(log, debug));
}


