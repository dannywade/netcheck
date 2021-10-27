from pyats.easypy import run
from genie import testbed


def main(runtime):

    temp_tb = "./temp_testbed/testbed.yaml"
    loaded_tb = testbed.load(temp_tb)
    run(testscript="testscripts/switch_install.py", runtime=runtime, testbed=loaded_tb)
