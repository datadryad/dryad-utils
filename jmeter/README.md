Dryad Load Tests for JMeter
=============================

This directory contains a set of load tests for use with Apache JMeter.

To use: 
1. Install JMeter
2. Run `bin/jmeter` to start the GUI, and open the file with load tests.
3. Press the green Run button to run all of the tests, OR right click on a test or scenario and choose Start.

The JMeter documentation suggests running tests from the command line -- in practice this makes little difference. But it can be done with:
```
bin/jmeter -n -t basicDryadTests.jmx 
```

Currently all tests are set to run on `secundus.datadryad.org`. To change this, run `bin/jmeter` to get into GUI mode, open the test file, expand the tree under a scenario, choose HTTP Request Defaults, and edit the Server Name.
