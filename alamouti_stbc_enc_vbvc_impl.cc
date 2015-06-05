/* -*- c++ -*- */
/* 
 * Copyright 2015 <+YOU OR YOUR COMPANY+>.
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
#include "alamouti_stbc_enc_vbvc_impl.h"

namespace gr {
  namespace uconn {

    alamouti_stbc_enc_vbvc::sptr
    alamouti_stbc_enc_vbvc::make()
    {
      return gnuradio::get_initial_sptr
        (new alamouti_stbc_enc_vbvc_impl());
    }

    /*
     * The private constructor
     * One input port of type char (byte)
     *    (each input item is a vector of two bytes)
     * Two output ports, each uses a complex type
     *    (each output item is a vector of two complex samples)
     */
    alamouti_stbc_enc_vbvc_impl::alamouti_stbc_enc_vbvc_impl()
      : gr::sync_block("alamouti_stbc_enc_vbvc",
              gr::io_signature::make(1, 1, 2 * sizeof(char)),
              gr::io_signature::make(2, 2, 2 * sizeof(gr_complex)))
    {
      // Initialize a symbol map for QPSK
      // Inputs are 'symbols', which can be created by packing two bits, e.g.
      // using the GNU Radio 'pack_k_bits_bb' function with an argument of 2.
      // This will be demonstrated in the Python QA code for this block.
      // (see qa_alamouti_stbc_enc_vbvc.py)
      qpsk_map[0] = gr_complex(1, 1);     // Bits 00 --> Symbol 0 --> (+1 + 1j)
      qpsk_map[1] = gr_complex(1, -1);    // Bits 01 --> Symbol 1 --> (+1 - 1j)
      qpsk_map[2] = gr_complex(-1, 1);    // Bits 10 --> Symbol 2 --> (-1 + 1j)
      qpsk_map[3] = gr_complex(-1, -1);   // Bits 11 --> Symbol 3 --> (-1 - 1j)
    }

    /*
     * Our virtual destructor.
     */
    alamouti_stbc_enc_vbvc_impl::~alamouti_stbc_enc_vbvc_impl()
    {
    }

    // -------------------------------------------------------------------------
    // Reference for the algorithm implemented by work()
    // -------------------------------------------------------------------------
    // [1] S. Alamouti, 'A Simple Transmit Diversity Technique for Wireless
    // Communications,' IEEE Journal on Select Areas in Communications,
    // Vol. 16, No. 8, October 1998.
    // -------------------------------------------------------------------------

    int
    alamouti_stbc_enc_vbvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        // Input data: bytes
        const char *in = (const char *) input_items[0];

        // Output data: complex (note there is one for each output port)
        gr_complex *out_0 = (gr_complex *) output_items[0];
        gr_complex *out_1 = (gr_complex *) output_items[1];

        // Process each input item. One input item is a vector of two bytes,
        // where the value of the bytes are 0, 1, 2, or 3 (since they each map
        // to one of the four possible QPSK symbols). For each input item, we
        // make one set of output items, where a set is 2 (since there are two
        // output ports). Also note that noutput_items is an argument to the
        // work() function - this is set by the scheduler, and can be any
        // integerer - so your block has to be designed to process any number
        // of input items!
        for (i = 0; i < noutput_items; ++i)
        {
          // Get the two input symbols, and map both to complex QPSK symbols
          // s0 = symbol at time (t)
          // s1 = symbol at time (t + Tsym)
          s0 = qpsk_map[in[2 * i]];
          s1 = qpsk_map[in[(2 * i) + 1]];

          // Create output 0 (for antenna 0)
          // This is encoded as described by [1], Table 1
          out_0[2 * i] = s0;
          out_0[(2 * i) + 1] = -std::conj(s1);

          // Create output 1 (for antenna 1)
          // This is encoded as described by [1], Table 1
          out_1[2 * i] = s1;
          out_1[(2 * i) + 1] = std::conj(s0);
        }

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace uconn */
} /* namespace gr */

