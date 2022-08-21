"""Testscript used to check the OSPF routing protocol."""
from pyats import aetest
import logging

logger = logging.getLogger(__name__)


class OSPFTest(aetest.Testcase):
    logging.info("OSPF testcase imported.")

    @aetest.test
    def ospf_test1(self):
        print("This is OSPF Test 1")
