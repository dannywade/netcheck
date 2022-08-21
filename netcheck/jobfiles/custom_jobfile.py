from pyats.easypy import run


def main(runtime):

    run(
        testscript="testscripts/custom_main.py",
        runtime=runtime,
    )
