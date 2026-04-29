# Copyright (c) 2025 Prodrive Technologies New Energies B.V.
# This code is licensed under MIT license (see LICENSE for details)

from pyModbusTCP.client import ModbusClient
from typing import Any
from .registers import ModbusAddress, ModbusAddresses

READ_COIL_RANGE = (0, 10_000)
DISCRETE_INPUT_RANGE = (10_000, 20_000)
INPUT_REGISTER_RANGE = (30_000, 40_000)
HOLDING_REGISTER_RANGE = (40_000, 50_000)


def in_range(value: int, range: tuple[int, int]):
    start, end = range
    return start <= value < end


class Modbus():
    def __init__(self, host: str, port: int = 502):
        self._c = ModbusClient(host=host, port=port, auto_open=True)

    def read(self, addr: ModbusAddress | ModbusAddresses):
        if isinstance(addr, ModbusAddresses):
            addr = addr.value

        assert addr.decoder is not None, "No decoder available for this address. Read likely not supported"

        if in_range(addr.address, READ_COIL_RANGE):
            func = self._c.read_coils
        elif in_range(addr.address, DISCRETE_INPUT_RANGE):
            raise NotImplementedError("Discrete input not yet implemented")
        elif in_range(addr.address, INPUT_REGISTER_RANGE):
            func = self._c.read_input_registers
        elif in_range(addr.address, HOLDING_REGISTER_RANGE):
            func = self._c.read_holding_registers
        else:
            raise NotImplementedError("Address out of range")

        val = func(addr.address, addr.size)
        if val:
            return addr.decoder(val)
        else:
            raise ValueError

    def write(self, addr: ModbusAddress | ModbusAddresses, data: Any):
        if isinstance(addr, ModbusAddresses):
            addr = addr.value

        assert addr.encoder is not None, "No encoder available for this address. Write not supported"

        encoded_data = addr.encoder(data)

        if addr.size != 1:
            resp = self._c.write_multiple_registers(addr.address, encoded_data)
        else:
            resp = self._c.write_single_register(addr.address, encoded_data[0])

        if not resp:
            raise ValueError
