#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, gr_unittest
from gnuradio import blocks
import uconn_swig as uconn

# ------------------------------------------------------------------------------
# Reference for the algorithm
# ------------------------------------------------------------------------------
# [1] S. Alamouti, 'A Simple Transmit Diversity Technique for Wireless
# Communications,' IEEE Journal on Select Areas in Communications,
# Vol. 16, No. 8, October 1998.
# ------------------------------------------------------------------------------

class qa_alamouti_stbc_enc_vbvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):

    	# This test inputs symbols (bytes) to the function and makes sure the
    	# basic functionality is correct (for one input, I get the right output)

    	# ----------------------------------------------------------------------
    	# Define input and expected output
    	# ----------------------------------------------------------------------

    	# Input: symbol 0 (bits 00) and symbol 1 (bits 01)
    	src_data = (0, 1)

    	# Expected result - from Alamouti's paper [1]
    	# Symbol 0 maps to (1 + 1j) and symbol 1 maps to (1 - 1j)
    	# From Table 1 in Alamouti's paper, we know exactly what should be
    	# produced by this block. The first two symbols (first row) are from 
    	# antenna 0, and the second two symbols (second row) are from antenna 1. 
    	# This makes it possible to test the block with a single unittest case.
    	expected_result = ((1 + 1j), (-1 - 1j), \
    					   (1 - 1j), (1 - 1j))

    	# ----------------------------------------------------------------------
    	# Initialize our GNU Radio blocks
    	# ----------------------------------------------------------------------

    	# Create a GNU Radio source: this block is only used for debugging
    	# The second argument is set to False so the data doesn't repeat, so
    	# only one period of our input is created by this block. Note the type
    	# is byte, which is denoted by _b in the function name.
    	src = blocks.vector_source_b(src_data, False)

    	# Create a block for organizing the input as a vector of two bytes,
    	# which is what the Alamouti encoder expects. Note that our source block
    	# is has vector_source in the name, but it actually creates streaming
    	# data (where each item is a single sample). The first argument to this
    	# function tells GNU Radio that our data type is a char (byte) and the
    	# second argument tells it to group 2 bytes together from the input
    	# stream, and output a single vector containing those two bytes.
    	stream_to_vec = blocks.stream_to_vector(gr.sizeof_char, 2)

    	# Initialize our Alamouti encoder - no input arguments
    	alamouti_enc = uconn.alamouti_stbc_enc_vbvc()

    	# At the output of our encoder, we'll need to convert from vectors to
    	# streams. This is done by two separate blocks, which are initialized
    	# here. Note that these work on complex types. The output of these will
    	# be fed into the two antenna ports.
    	vec_to_stream_ant_0 = blocks.vector_to_stream(gr.sizeof_gr_complex, 2)
    	vec_to_stream_ant_1 = blocks.vector_to_stream(gr.sizeof_gr_complex, 2)

    	# Finally, create two sinks (each can resemble an antenna port)
    	# Note the _c in the function name (for complex type).
    	ant_0_snk = blocks.vector_sink_c()
    	ant_1_snk = blocks.vector_sink_c()

    	# ----------------------------------------------------------------------
    	# Connect up our test bench (a GNU Radio flowgraph)
    	# ----------------------------------------------------------------------

    	# Source --> Stream to Vector --> Alamouti Encoder
    	self.tb.connect(src, stream_to_vec, alamouti_enc)

    	# Alamouti Encoder Antenna 0 --> Vector to Stream --> Antenna 0 Sink
    	self.tb.connect((alamouti_enc, 0), vec_to_stream_ant_0, ant_0_snk)

    	# Alamouti Encoder Antenna 1 --> Vector to Stream --> Antenna 1 Sink
    	self.tb.connect((alamouti_enc, 1), vec_to_stream_ant_1, ant_1_snk)

    	# ----------------------------------------------------------------------
    	# Run the test
    	# ----------------------------------------------------------------------

        self.tb.run ()

        # ----------------------------------------------------------------------
    	# Check the result
    	# ----------------------------------------------------------------------

    	# Pull the resulting data from the antenna sinks
    	ant_0_data = ant_0_snk.data()
    	ant_1_data = ant_1_snk.data()

    	# Format the output so we can compare it to our expected output
    	# (note that adding two tuples concatenates them)
    	result_data = ant_0_data + ant_1_data

    	# Function for testing equivalence of two complex tuples
    	self.assertComplexTuplesAlmostEqual(expected_result, result_data, 6)

    def test_002_t (self):

    	# This test is similar to the first test, only now we're inputing bits
    	# and packing them into bytes (symbols) externally to the Alamouti
    	# encoder.

    	# Input: all four symbols in order (0, 1, 2, 3), as bits
    	# Note that this will create two space time symbols
    	src_data = (0, 0, 0, 1, 1, 0, 1, 1)

    	# Expected result - from Alamouti's paper [1]
    	# The first two rows are from antenna 0
    	# The second two rows are from antenna 1
    	# Within those two rows, the columns correspond to time instants
    	expected_result = ((1 + 1j), (-1 - 1j), \
    					   (-1 + 1j), (1 - 1j), \
    					   (1 - 1j), (1 - 1j), \
    					   (-1 - 1j), (-1 - 1j))

    	# ----------------------------------------------------------------------
    	# Initialize our GNU Radio blocks
    	# ----------------------------------------------------------------------

    	# Create a GNU Radio source: this block is only used for debugging
    	# The second argument is set to False so the data doesn't repeat, so
    	# only one period of our input is created by this block. Note the type
    	# is byte, which is denoted by _b in the function name.
    	src = blocks.vector_source_b(src_data, False)

    	# Block for packing two bits into a symbol byte
    	packer = blocks.pack_k_bits_bb(2)

    	# Create a block for organizing the input as a vector of two bytes,
    	# which is what the Alamouti encoder expects. Note that our source block
    	# is has vector_source in the name, but it actually creates streaming
    	# data (where each item is a single sample). The first argument to this
    	# function tells GNU Radio that our data type is a char (byte) and the
    	# second argument tells it to group 2 bytes together from the input
    	# stream, and output a single vector containing those two bytes.
    	stream_to_vec = blocks.stream_to_vector(gr.sizeof_char, 2)

    	# Initialize our Alamouti encoder - no input arguments
    	alamouti_enc = uconn.alamouti_stbc_enc_vbvc()

    	# At the output of our encoder, we'll need to convert from vectors to
    	# streams. This is done by two separate blocks, which are initialized
    	# here. Note that these work on complex types. The output of these will
    	# bed fed into the two antenna ports.
    	vec_to_stream_ant_0 = blocks.vector_to_stream(gr.sizeof_gr_complex, 2)
    	vec_to_stream_ant_1 = blocks.vector_to_stream(gr.sizeof_gr_complex, 2)

    	# Finally, create two sinks (each can resemble an antenna port)
    	# Note the _c in the function name (for complex type).
    	ant_0_snk = blocks.vector_sink_c()
    	ant_1_snk = blocks.vector_sink_c()

    	# ----------------------------------------------------------------------
    	# Connect up our test bench (a GNU Radio flowgraph)
    	# ----------------------------------------------------------------------

    	# Source --> Bit Packer --> Stream to Vector --> Alamouti Encoder
    	self.tb.connect(src, packer, stream_to_vec, alamouti_enc)

    	# Alamouti Encoder Antenna 0 --> Vector to Stream --> Antenna 0 Sink
    	self.tb.connect((alamouti_enc, 0), vec_to_stream_ant_0, ant_0_snk)

    	# Alamouti Encoder Antenna 1 --> Vector to Stream --> Antenna 1 Sink
    	self.tb.connect((alamouti_enc, 1), vec_to_stream_ant_1, ant_1_snk)

    	# ----------------------------------------------------------------------
    	# Run the test
    	# ----------------------------------------------------------------------

        self.tb.run ()

        # ----------------------------------------------------------------------
    	# Check the result
    	# ----------------------------------------------------------------------

    	# Pull the resulting data from the antenna sinks
    	ant_0_data = ant_0_snk.data()
    	ant_1_data = ant_1_snk.data()

    	# Format the output so we can compare it to our expected output
    	# (note that adding two tuples concatenates them)
    	result_data = ant_0_data + ant_1_data

    	# Function for testing equivalence of two complex tuples
    	self.assertComplexTuplesAlmostEqual(expected_result, result_data, 6)

if __name__ == '__main__':
    gr_unittest.run(qa_alamouti_stbc_enc_vbvc, "qa_alamouti_stbc_enc_vbvc.xml")
