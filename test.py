#!/usr/bin/env python
import coverage
COV = coverage.coverage(branch=True, include='fra/*')
COV.start()

import unittest
from tests import suite
unittest.TextTestRunner(verbosity=2).run(suite)

COV.stop()
COV.report()
