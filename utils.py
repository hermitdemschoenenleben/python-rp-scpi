class RedPitayaChild:
    def __init__(self, rp):
        self._rp = rp


def _idx_cmd(commands):
    def getter(self):
        return [cmd.format(idx=self.idx, value='{value}') for cmd in commands]
    return property(getter)


def _getter(cmd):
    def wrapper(fct):
        def getter(self):
            self._rp._cmd(cmd.fget(self)[0])
            return fct(self, self._rp._read())

        return property(getter)

    return wrapper


def _simple_getter(cmd):
    @_getter(cmd)
    def getter(self, value):
        return value

    return getter


def _setter(cmd, getter):
    def wrapper(fct):
        @getter.setter
        def setter(self, value):
            self._rp._cmd(cmd.fget(self)[1].format(value=fct(self, value)))

        return setter
    return wrapper


def _simple_setter(cmd, getter):
    @_setter(cmd, getter)
    def setter(self, value):
        return value
    return setter


def _simple_getter_and_setter(cmd):
    return _simple_setter(cmd, _simple_getter(cmd))


def _buffer_to_array(buffer):
    return [
        float(value)
        for value in buffer \
            .lstrip('{') \
            .rstrip('}') \
            .split(',')
        if value
    ]
