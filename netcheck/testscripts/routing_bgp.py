"""Testscript used to check the BGP routing protocol."""
from pyats import aetest
import logging

logger = logging.getLogger(__name__)


class BGPTest(aetest.Testcase):
    logging.info("BGP testcase imported.")

    @aetest.test
    def bgp_test1(self):
        logging.info("This is BGP Test 1")
