"""Testscript used to check the OSPF routing protocol."""
from pyats import aetest
import logging

logger = logging.getLogger(__name__)


class OSPFTest(aetest.Testcase):
    groups = ["ospf"]
    logging.info("OSPF testcase")
