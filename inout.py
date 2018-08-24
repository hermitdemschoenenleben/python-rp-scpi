from .utils import RedPitayaChild, _simple_getter_and_setter, _idx_cmd


class AnalogOutput(RedPitayaChild):
    def __init__(self, rp, idx):
        self.idx = idx
        super(AnalogOutput, self).__init__(rp)

    _cmd = dict((k, _idx_cmd(cmd)) for k, cmd in {
        'voltage': ('ANALOG:PIN? AOUT{idx}', 'ANALOG:PIN AOUT{idx},{value}')
    }.items())

    voltage = _simple_getter_and_setter(_cmd['voltage'])


class Input(RedPitayaChild):
    def __init__(self, rp, idx):
        self.idx = idx
        super(Input, self).__init__(rp)

    _cmd = dict((k, _idx_cmd(cmd)) for k, cmd in {
        'voltage': ('ANALOG:PIN? AIN{idx}', 'ANALOG:PIN AIN{idx},{value}')
    }.items())

    voltage = _simple_getter_and_setter(_cmd['voltage'])


class DigitalInputOutput(RedPitayaChild):
    def __init__(self, rp, pin):
        self.pin = pin
        super(DigitalInputOutput, self).__init__(rp)

    def set_direction(self, direction):
        assert direction in ['INP', 'OUT']
        self._rp._cmd('DIG:PIN:DIR %s,%s' % (direction, self.pin))

    @property
    def value(self):
        self._rp._cmd('DIG:PIN? %s' % self.pin)
        return int(self._rp._read())

    @value.setter
    def value(self, value):
        self._rp._cmd('DIG:PIN %s,%d' % (self.pin, 1 if value else 0))
