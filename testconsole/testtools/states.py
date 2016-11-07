from testtools.testresult.real import STATES


for state in STATES:
    if state is not None:
        globals()[state.upper()] = state
