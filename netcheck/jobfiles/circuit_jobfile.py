from pyats.easypy import run
from genie import testbed

def main(runtime):
    
    # TODO: Need to load testbed from DB or file
    temp_tb = "./temp_testbed/testbed.yaml"
    loaded_tb = testbed.load(temp_tb)
    run(testscript = 'testscripts/circuit_upgrade.py', runtime=runtime, testbed=loaded_tb)