import numpy as np
from paramiko import SSHClient, AutoAddPolicy
from .utils import RedPitayaChild


MONITOR_PATH = '/opt/redpitaya/bin/monitor'
SIGNAL_REGISTER_BASE = 0x40200000
PID_REGISTER_BASE = 0x40300000


def to_hex(number):
    return "{0:#0{1}x}".format(number, 10)


def from_hex(number):
    return int(number, 0)


class RedPitayaRegisters(RedPitayaChild):
    _client = None

    @property
    def ssh(self):
        if self._client is None:
            self._client = SSHClient()
            self._client.set_missing_host_key_policy(AutoAddPolicy())
            self._client.connect(self._rp.ip, username='root',
                                 password='root')

        return self._client

    def execute(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        return stdin, stdout, stderr

    def get_register_id(self, base, register_offset):
        return hex(base + register_offset)

    def set_register(self, base, register_offset, value):
        register = self.get_register_id(base, register_offset)
        #print('CMD', '%s %s %s' % (MONITOR_PATH, register, to_hex(value)))
        self.execute('%s %s %s' % (MONITOR_PATH, register, to_hex(value)))

    def get_register(self, base, register_offset):
        register = self.get_register_id(base, register_offset)
        #print('GET', register)
        _, stdout, _2 = self.execute('%s %s' % (MONITOR_PATH, register))
        return from_hex(stdout.read().decode().rstrip('\n'))

    def pid_integrator_reset(self, values):
        """
        Resets integrators. `values` is a 4-element of booleans
        """
        register = 0

        number = 0
        for i, v in enumerate(values):
            if v:
                number += 2 ** i

        # check that we only write the first digit
        number = number & 0xf
        data = self.get_register(PID_REGISTER_BASE, register) & 0xfffffff0
        self.set_register(PID_REGISTER_BASE, register, data + number)

    def pid_set_setpoint(self, channel, value):
        assert abs(value) < 8191, 'value too high'
        assert channel < 4, 'channel has to be between 0 and 3'

        register = (channel + 1) << 4
        data = self.get_register(PID_REGISTER_BASE, register) & 0xffff0000
        if value < 0:
            value = 16384 + value

        value = value & 0xffff

        self.set_register(PID_REGISTER_BASE, register, data + value)

    def pid_set_p(self, channel, value):
        assert abs(value) < 8191, 'value too high'
        assert channel < 4, 'channel has to be between 0 and 3'

        register = ((channel + 1) << 4) + 4
        data = self.get_register(PID_REGISTER_BASE, register) & 0xffff0000
        if value < 0:
            value = 16384 + value

        value = value & 0xffff

        self.set_register(PID_REGISTER_BASE, register, data + value)

    def pid_set_i(self, channel, value):
        assert abs(value) < 8191, 'value too high'
        assert channel < 4, 'channel has to be between 0 and 3'

        register = ((channel + 1) << 4) + 8
        data = self.get_register(PID_REGISTER_BASE, register) & 0xffff0000
        if value < 0:
            value = 16384 + value

        value = value & 0xffff

        self.set_register(PID_REGISTER_BASE, register, data + value)

    def pid_set_d(self, channel, value):
        assert abs(value) < 8191, 'value too high'
        assert channel < 4, 'channel has to be between 0 and 3'

        register = ((channel + 1) << 4) + 12
        data = self.get_register(PID_REGISTER_BASE, register) & 0xffff0000
        if value < 0:
            value = 16384 + value

        value = value & 0xffff

        self.set_register(PID_REGISTER_BASE, register, data + value)

    def set_offset(self, channel, offset):
        assert channel < 2, 'channel has to be 0 or 1'
        assert abs(offset) <= 1

        mask = 0b11111111111111
        negative_mask = 0b11000000000000001111111111111111
        bit_shift = 16
        register = 0x4 if channel == 0 else 0x24

        data = self.get_register(SIGNAL_REGISTER_BASE, register)
        offset_data = (data >> bit_shift) & mask
        offset_cnt = int(offset * 8191)
        if offset_cnt < 0:
            offset_cnt = (8192*2) + offset_cnt
        new_offset_data = (offset_cnt) & mask
        new_data = (data & negative_mask) + (new_offset_data << 16)
        self.set_register(SIGNAL_REGISTER_BASE, register, new_data)

    def acquire(self, number):
        stdin, stdout, stderr = self.execute('/opt/redpitaya/bin/acquire %d' % number)

        lines = [
            line.strip().split(' ')
            for line in stdout.readlines()
        ]
        to_voltage = lambda x: float(x) / 8191
        data = [
            [to_voltage(line[0]), to_voltage(line[-1])]
            for line in lines
        ]
        return np.array(data)
