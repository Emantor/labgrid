from pprint import pprint

import attr
import jinja2
import os

from ..util.yaml import load
from ..exceptions import NoConfigFoundError


@attr.s(eq=False)
class ResourceConfig:
    filename = attr.ib(validator=attr.validators.instance_of(str))

    def __attrs_post_init__(self):
        env = jinja2.Environment(
            line_statement_prefix='#',
            line_comment_prefix='##',
        )
        try:
            with open(self.filename) as file:
                template = env.from_string(file.read())
        except FileNotFoundError:
            raise NoConfigFoundError(
                "{} could not be found".format(self.filename)
            )
        rendered = template.render(env=os.environ)
        pprint(('rendered', rendered))
        self.data = load(rendered)
        pprint(('loaded', self.data))
