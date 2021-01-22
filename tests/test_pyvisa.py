from importlib.util import find_spec

from labgrid.resource.pyvisa import PyVISADevice
from labgrid.driver.pyvisadriver import PyVISADriver

import pytest

pytestmark = pytest.mark.skipif(not find_spec("pyvisa"),
                              reason="crossbar required")

def test_pyvisa_resource(target):
    PyVISADevice(target, name=None, type='TCPIP', url='127.0.0.1')


def test_resource_driver(target, mocker):
    PyVISADevice(target, name=None, type='TCPIP', url='127.0.0.1')
    driver = PyVISADriver(target, name=None)

    mocker.patch('pyvisa.ResourceManager.open_resource', return_value=None)
    target.activate(driver)
