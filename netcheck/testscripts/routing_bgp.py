"""Testscript used to check the BGP routing protocol."""
from pyats import aetest
import logging

logger = logging.getLogger(__name__)


class BGPTest(aetest.Testcase):
    groups = ["bgp"]
    logging.info("BGP testcase")
