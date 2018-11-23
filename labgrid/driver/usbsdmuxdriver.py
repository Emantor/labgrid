# pylint: disable=no-member
import subprocess
import attr

from .common import Driver
from ..factory import target_factory
from ..resource.remote import NetworkUSBSDMuxDevice
from ..resource.udev import USBSDMuxDevice
from ..step import step
from ..protocol import BootstrapProtocol
from .exception import ExecutionError
from ..util.managedfile import ManagedFile

@target_factory.reg_driver
@attr.s(cmp=False)
class USBSDMuxDriver(Driver, BootstrapProtocol):
    """The USBSDMuxDriver uses the usbsdmux tool
    (https://github.com/pengutronix/usbsdmux) to control the USB-SD-Mux
    hardware

    Args:
        bindings (dict): driver to use with usbsdmux
    """
    bindings = {
        "mux": {USBSDMuxDevice, NetworkUSBSDMuxDevice},
    }

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if self.target.env:
            self.tool = self.target.env.config.get_tool('usbsdmux') or 'usbsdmux'
        else:
            self.tool = 'usbsdmux'

    @Driver.check_active
    @step(title='sdmux_set', args=['mode'])
    def set_mode(self, mode):
        if not mode.lower() in ['dut', 'host', 'off', 'client']:
            raise ExecutionError("Setting mode '%s' not supported by USBSDMuxDriver" % mode)
        cmd = self.mux.command_prefix + [
            self.tool,
            "-c",
            self.mux.control_path,
            mode.lower()
        ]
        subprocess.check_call(cmd)

    @Driver.check_active
    @step(args=["filename"])
    def load(self, filename):
        if not self.mux.path:
            raise ExecutionError("SDMux ist not in host mode")
        mf = ManagedFile(filename, self.mux)
        mf.sync_to_resource()

        cmd = self.mux.command_prefix + [
            'cp',
            mf.get_remote_path(),
            self.mux.path
        ]

        subprocess.check_call(cmd)

