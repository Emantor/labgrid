import base64
import json
import os
import sys
from datetime import datetime

from .step import steps
from .driver import Driver
from .resource import Resource


class JSONLoggingReporter:
    """JSONLoggingReporter - Reporter that writes JSON step information

    Args:
        logpath (str): path to store the logfiles in
    """
    instance = None

    @classmethod
    def start(cls, path):
        """starts the ConsoleLoggingReporter"""
        assert cls.instance is None
        cls.instance = cls(path)

    @classmethod
    def stop(cls):
        """stops the ConsoleLoggingReporter"""
        assert cls.instance is not None
        cls.instance._stop()
        steps.unsubscribe(cls.instance.notify)
        cls.instance = None

    def __init__(self, logpath):
        if logpath:
            self.logfile = open("{}/labgrid.json".format(logpath), 'bw')
        else:
            self.logfile = open("labgrid.json", 'bw')
        steps.subscribe(self.notify)

    def _stop(self):
        self.logfile.close()

    def notify(self, event):
        """This is the callback function for steps"""
        data = {'ts': event.ts, 'event': "{}".format(event)}
        if event.step:
            data['step'] = {}
            data['title'] = event.step.title
            if event.step.result:
                if isinstance(event.step.result, (bytes, bytearray)):
                    data['result'] = event.step.result.decode('utf-8')
                if isinstance(event.step.result, (tuple)):
                    data['result'] = event.step.result.decode('utf-8')
                else:
                    data['result'] = event.step.result
            if event.step.source:
                if isinstance(event.step.source, (Driver, Resource)):
                    data['target'] = event.step.source.target.name
        self.logfile.write(b'\x1e')
        self.logfile.write(json.dumps(data).encode('utf-8'))
        self.logfile.write(b'\n')
