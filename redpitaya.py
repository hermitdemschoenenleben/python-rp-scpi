from .redpitaya_scpi import scpi
from .fast_inout import FastIn, FastOut
from .inout import Input, AnalogOutput, DigitalInputOutput
from .registers import RedPitayaRegisters


class RedPitaya:
    """
    Connects to a red pitaya via ethernet.
    Warning: This class is incomplete and just provides access to things I needed.

    Usage:

        rp = RedPitaya(ip_address)

        # generate a 1000Hz, 1V sine wave on fast out 1
        rp.fast_out[0].enabled = True
        rp.fast_out[0].offset = 1
        rp.fast_out[0].amplitude = 1
        rp.fast_out[0].wave_form = 'SINE'
        rp.fast_out[0].frequency = 1000

        # if you want a static voltage at a fast output:
        rp.fast_out[0].set_constant_voltage(0.5)

        # read a single value of fast in 1
        print(rp.fast_in[0].get_value())

        # wait for a trigger on fast in 2 and print the buffer of fast in 1
        rp.set_acquisition_trigger('CH2_PE', decimation=DECIMATION_FACTOR, delay=8192)

        while not rp.was_triggered():
            sleep(0.1)

        print(rp.fast_in[0].get_buffer())

        # sets a digital slow output
        rp.digital_inout['DIO0_N'].set_direction('OUT')
        rp.digital_inout['DIO0_N'].value = 1

        # reads a digital slow input
        rp.digital_inout['DIO0_N'].set_direction('INP')
        print(rp.digital_inout['DIO0_N'].value)

        # sets an analog slow output
        rp.analog_output(0).voltage = 0.5
    """
    _connection = None

    def __init__(self, ip='rp-f012ba.local', delay_scpi_connection=False):
        self.ip = ip

        if not delay_scpi_connection:
            # this forces the connection
            self.connection

        self.fast_out = [FastOut(self, idx + 1) for idx in range(2)]
        self.fast_in = [FastIn(self, idx + 1) for idx in range(2)]
        self.analog_output = [AnalogOutput(self, idx) for idx in range(4)]
        inout_channels = [
            item for sublist in [
                ['DIO%d_N' % idx, 'DIO%d_P' % idx] for idx in range(8)
            ]
            for item in sublist
        ]
        self.digital_inout = dict([
            (k, DigitalInputOutput(self, k))
            for k in inout_channels
        ])
        self.input = [Input(self, idx) for idx in range(4)]
        self.registers = RedPitayaRegisters(self)

    @property
    def connection(self):
        if self._connection is None:
            try:
                self._connection = scpi(self.ip)
            except Exception:
                raise ConnectionError('unable to connect to ip %s. Is SCPI application started on red pitaya?' % self.ip)
        return self._connection

    def _cmd(self, cmd):
        return self.connection.tx_txt(cmd)

    def _read(self):
        return self.connection.rx_txt()

    def start_acquisition(self):
        self._cmd('ACQ:START')

    def stop_acquisition(self):
        self._cmd('ACQ:STOP')

    def set_acquisition_trigger(self, value, level=0, decimation=1, delay=0):
        assert value in ('DISABLED', 'NOW', 'CH1_PE', 'CH1_NE', 'CH2_PE',
                         'CH2_NE', 'EXT_PE', 'EXT_NE', 'AWG_PE', 'AWG_NE'), \
            'invalid trigger value'

        self._cmd('ACQ:RST')
        self._cmd('ACQ:DEC %d' % decimation)
        self._cmd('ACQ:TRIG:LEV %d' % level)
        self._cmd('ACQ:TRIG:DLY %d' % delay)
        self._cmd('ACQ:START')
        # TODO: Sleep necessary?
        # print('SLEEPING')
        # from time import sleep
        # sleep(1)
        self._cmd('ACQ:TRIG %s' % value)

    def was_triggered(self):
        self._cmd('ACQ:TRIG:STAT?')
        if 'TD' in self._read():
            return True
        return False


class ConnectionError(Exception):
    pass


class RedPitayaError(Exception):
    pass
