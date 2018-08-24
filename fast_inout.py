from .utils import RedPitayaChild, _idx_cmd, _simple_getter, _simple_setter, \
    _buffer_to_array, _getter, _setter


class FastIn(RedPitayaChild):
    def __init__(self, rp, idx):
        self.idx = idx
        super(FastIn, self).__init__(rp)

    def get_value(self):
        """Retrieve a single value"""
        self._rp.set_acquisition_trigger('NOW')
        self._rp._cmd('ACQ:SOUR%d:DATA:STA:N? 1,1' % self.idx)
        return _buffer_to_array(self._rp._read())[0]

    def read_buffer(self):
        self._rp._cmd('ACQ:SOUR%d:DATA?' % self.idx)
        return _buffer_to_array(self._rp._read())


class FastOut(RedPitayaChild):
    _cmd = dict((k, _idx_cmd(cmd)) for k, cmd in {
        'enabled': ('OUTPUT{idx}:STATE?', 'OUTPUT{idx}:STATE {value}'),
        'wave_form': ('SOUR{idx}:FUNC?', 'SOUR{idx}:FUNC {value}'),
        'frequency': ('SOUR{idx}:FREQ:FIX?', 'SOUR{idx}:FREQ:FIX {value}'),
        'amplitude': ('SOUR{idx}:VOLT?', 'SOUR{idx}:VOLT {value}'),
        'offset': ('SOUR{idx}:VOLT:OFFS?', 'SOUR{idx}:VOLT:OFFS {value}'),
        'phase': ('SOUR{idx}:PHAS?', 'SOUR{idx}:PHAS {value}'),
    }.items())

    def __init__(self, rp, idx):
        self.idx = idx
        super(FastOut, self).__init__(rp)

    @_getter(_cmd['enabled'])
    def enabled(self, value):
        return value in ('1', 'ON')

    @_setter(_cmd['enabled'], enabled)
    def enabled(self, value):
        return 'ON' if value else 'OFF'

    wave_form = _simple_getter(_cmd['wave_form'])

    @_setter(_cmd['wave_form'], wave_form)
    def wave_form(self, value):
        return str(value).upper()

    @_getter(_cmd['frequency'])
    def frequency(self, value):
        return float(value)
    frequency = _simple_setter(_cmd['frequency'], frequency)

    @_getter(_cmd['amplitude'])
    def amplitude(self, value):
        return float(value)
    amplitude = _simple_setter(_cmd['amplitude'], amplitude)

    @_getter(_cmd['offset'])
    def offset(self, value):
        return float(value)
    offset = _simple_setter(_cmd['offset'], offset)

    @_getter(_cmd['phase'])
    def phase(self, value):
        return float(value)
    phase = _simple_setter(_cmd['phase'], phase)

    def set_constant_voltage(self, voltage):
        self.frequency = 0
        self.amplitude = 0
        self.phase = 0
        self.wave_form = 'SINE'
        self.offset = voltage
        self.enabled = True
