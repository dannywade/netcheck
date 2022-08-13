from pyats.easypy import run
from genie import testbed


def main(runtime):

    # TODO: Read in YAML datafile for each task (testscript)

    temp_tb = "./temp_testbed/testbed.yaml"
    loaded_tb = testbed.load(temp_tb)
    run(
        testscript="testscripts/environment.py",
        runtime=runtime,
        taskid="environment",
        testbed=loaded_tb,
    )
    run(
        testscript="testscripts/routing_bgp.py",
        runtime=runtime,
        taskid="routing_bgp",
        testbed=loaded_tb,
    )
    run(
        testscript="testscripts/routing_ospf.py",
        runtime=runtime,
        taskid="routing_ospf",
        testbed=loaded_tb,
    )
