#!/usr/bin/env python3
# See LICENSE for licensing information.
#
# Copyright (c) 2016-2021 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#
"""
This script will functionally simulate an SRAM previously generated by OpenRAM 
given a configuration file. Configuration option "use_pex" determines whether 
extracted or generated spice is used. Command line arguments dictate the
number of cycles and period to be simulated.
"""

import sys
import datetime
from globals import *
from importlib import reload

(OPTS, args) = parse_args()

# Override the usage
USAGE = "Usage: {} [options] <config file> <cycles> <period>\nUse -h for help.\n".format(__file__)

# Check that we are left with a single configuration file as argument.
if len(args) != 3:
    print(USAGE)
    sys.exit(2)

# Parse argument
config_file = args[0]
cycles = int(args[1])
period = float(args[2])

# These depend on arguments, so don't load them until now.
import debug

# Parse config file and set up all the options
init_openram(config_file=config_file, is_unit_test=False)

print_banner()

# Configure the SRAM organization (duplicated from openram.py)
from sram_config import sram_config
c = sram_config(word_size=OPTS.word_size,
                num_words=OPTS.num_words,
                write_size=OPTS.write_size,
                num_banks=OPTS.num_banks,
                words_per_row=OPTS.words_per_row,
                num_spare_rows=OPTS.num_spare_rows,
                num_spare_cols=OPTS.num_spare_cols)

OPTS.netlist_only = True
OPTS.check_lvsdrc = False

# Initialize and create the sram object
from sram import sram
s = sram(name=OPTS.output_name, sram_config=c)

# Generate stimulus and run functional simulation on the design
start_time = datetime.datetime.now()
from characterizer import functional
debug.print_raw("Functional simulation... ")
f = functional(s.s, cycles=cycles, spfile=s.get_sp_name(), period=period, output_path=OPTS.openram_temp)
(fail, error) = f.run()
debug.print_raw(error)
print_time("Functional simulation", datetime.datetime.now(), start_time)

# Delete temp files, remove the dir, etc. after success
if fail:
    end_openram()
