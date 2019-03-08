#!/usr/bin/env python3
"""
Check the .lib file for an SRAM
"""

import unittest
from testutils import header,openram_test
import sys,os,re
sys.path.append(os.path.join(sys.path[0],".."))
import globals
from globals import OPTS
import debug

class lib_test(openram_test):

    def runTest(self):
        globals.init_openram("config_20_{0}".format(OPTS.tech_name))
        OPTS.analytical_delay = False
        OPTS.trim_netlist = False

        # This is a hack to reload the characterizer __init__ with the spice version
        from importlib import reload
        import characterizer
        reload(characterizer)
        from characterizer import lib
        if not OPTS.spice_exe:
            debug.error("Could not find {} simulator.".format(OPTS.spice_name),-1)

        from sram import sram
        from sram_config import sram_config
        c = sram_config(word_size=2,
                        num_words=16,
                        num_banks=1)
        c.words_per_row=1
        c.recompute_sizes()
        debug.info(1, "Testing timing for sample 2 bit, 16 words SRAM with 1 bank")

        # This doesn't have to use the factory since worst case
        # it will just replaece the top-level module of the same name
        s = sram(c, "sram_2_16_1_{0}".format(OPTS.tech_name))

        tempspice = OPTS.openram_temp + "temp.sp"
        s.sp_write(tempspice)

        lib(out_dir=OPTS.openram_temp, sram=s.s, sp_file=tempspice, use_model=False)

        # get all of the .lib files generated
        files = os.listdir(OPTS.openram_temp)
        nametest = re.compile("\.lib$", re.IGNORECASE)
        lib_files = filter(nametest.search, files)

        # and compare them with the golden model
        for filename in lib_files:
            libname = "{0}/{1}".format(OPTS.openram_temp,filename)
            golden = "{0}/golden/{1}".format(os.path.dirname(os.path.realpath(__file__)),filename)
            self.assertTrue(self.isapproxdiff(libname,golden,0.40))

        reload(characterizer)
        globals.end_openram()
        
# run the test from the command line
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()






