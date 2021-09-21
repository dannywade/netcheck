from pyats.easypy import run

def main(runtime):
    
    # TODO: Need to load testbed from DB or file
    
    run(testscript = 'testscripts/circuit_upgrade.py', runtime=runtime)