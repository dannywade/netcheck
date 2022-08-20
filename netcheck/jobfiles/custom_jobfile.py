from pyats.easypy import run
from genie import testbed


def main(runtime):

    # TODO: Read in YAML datafile for each task (testscript)

    temp_tb = "./temp_testbed/testbed.yaml"
    loaded_tb = testbed.load(temp_tb)
    run(
        testscript="testscripts/custom_main.py",
        runtime=runtime,
        testbed=loaded_tb,
    )
