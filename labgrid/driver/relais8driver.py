# pylint: disable=no-member
import subprocess
import attr

from ..factory import target_factory
from ..resource.udev import USBRelais8
from ..step import step
from .common import Driver
from ..protocol import DigitalOutputProtocol


@target_factory.reg_driver
@attr.s(cmp=False)
class Relais8Driver(Driver, DigitalOutputProtocol):
    bindings = {
        "relais": {USBRelais8},
    }

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if self.target.env:
            self.tool = self.target.env.config.get_tool(
                'relais8'
            ) or 'relais8ctl'
        else:
            self.tool = 'relais8ctl'

    def _get_relais8_prefix(self):
        return self.relais.command_prefix + [
            self.tool,
            self.relais.path,
        ]

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    @Driver.check_active
    @step(title='call', args=['args'])
    def __call__(self, *args):
        subprocess.check_call(self._get_relais8_prefix() + list(args))

    @Driver.check_active
    @step(args=['status'])
    def set(self, status):
        self("set_single", str(self.relais.port), "1" if status else "0")

    @Driver.check_active
    @step()
    def get(self):
        output = subprocess.check_output(
            self._get_relais8_prefix() +
            ["get_single", str(self.relais.port)]
        ).decode('utf-8')
        return True if 'True' in output else False
