import os
import unittest

from nose.plugins import PluginTester
from nose.plugins.skip import SkipTest
from nose.plugins.multiprocess import MultiProcess


support = os.path.join(os.path.dirname(__file__), 'support')


def setup():
    try:
        import multiprocessing
        if 'active' in MultiProcess.status:
            raise SkipTest("Multiprocess plugin is active. Skipping tests of "
                           "plugin itself.")
    except ImportError:
        raise SkipTest("multiprocessing module not available")


class TestMPNameError(PluginTester, unittest.TestCase):
    activate = '--processes=2'
    plugins = [MultiProcess()]
    suitepath = os.path.join(support, 'nameerror.py')

    def runTest(self):
        print str(self.output)
        assert 'NameError' in self.output
        assert "'undefined_variable' is not defined" in self.output

