#!/usr/bin/env python3

import queue
import logging
import threading
import time

import attr
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

from .common import Driver
from ..factory import target_factory
from ..protocol import PowerProtocol
from ..step import step
from ..util import Timeout


@target_factory.reg_driver
@attr.s(eq=False)
class TasmotaPowerDriver(Driver, PowerProtocol):
    bindings = {
            "power": {"TasmotaPowerPort", "NetworkTasmotaPowerPort"}
    }
    delay = attr.ib(default=2.0, validator=attr.validators.instance_of(float))
    _client = attr.ib(default=mqtt.Client(), validator=attr.validators.instance_of(mqtt.Client))
    _status_lock = attr.ib(default=threading.Lock())
    _status = attr.ib(default=None)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    def on_activate(self):
        self._client.on_message = self._on_message
        self._client.on_connect = self._on_connect
        self._client.connect(self.power.host)
        self._client.loop_start()

    def on_deactivate(self):
        self._client.loop_stop()

    def _on_message(self, client, userdata, msg):
        if msg.payload == b'ON':
            status = True
        elif msg.payload == b'OFF':
            status = False
        with self._status_lock:
            self._status = status

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.power.status_topic)

    @Driver.check_active
    @step()
    def on(self):
        self._client.publish(self.power.power_topic, payload="ON")

    @Driver.check_active
    @step()
    def off(self):
        self._client.publish(self.power.power_topic, payload="OFF")

    @Driver.check_active
    @step()
    def cycle(self):
        self.off()
        time.sleep(self.delay)
        self.on()

    def _get_status(self):
        with self._status_lock:
            status = self._status
        return status

    @Driver.check_active
    @step()
    def get(self):
        self._client.publish(self.power.power_topic)
        while self._status is None:
            time.sleep(0.1)
        return self._get_status()
