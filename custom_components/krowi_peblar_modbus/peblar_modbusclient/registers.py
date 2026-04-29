# Copyright (c) 2025 Prodrive Technologies New Energies B.V.
# This code is licensed under MIT license (see LICENSE for details)

from dataclasses import dataclass
from typing import Callable, Any
from pymodbus.client.mixin import ModbusClientMixin
from enum import Enum
from functools import partial


class CurrentLimitSource(Enum):
    UNKNOWN = 0
    FIXED_CABLE = 1
    THERMAL = 2
    CONFIGURATION_LIMIT = 3
    BOP = 4
    LOAD_BALANCING = 5
    USER_CABLE = 6
    OVERCURRENT_PROTECTION = 7
    HARDWARE_LIMIT = 8
    POWER_FACTOR = 9
    OCPP_SMART_CHARGING = 10
    VDE_PHASE_IMBALANCE = 11
    LOCAL_SCHEDULED_CHARGING = 12
    SOLAR_CHARGING = 13
    CURRENT_SLIDER = 14
    LOCAL_REST_API = 15
    LOCAL_MODBUS_API = 16
    POWER_LIMIT_INPUT = 17
    HOUSEHOLD_POWER_LIMIT = 18
    RESERVED = 19
    INTERNAL_POWER_LIMITER = 20


@dataclass
class ModbusAddress:
    address: int
    size: int
    encoder: Callable[[Any], list[int]] | None
    decoder: Callable[[(list[int] | list[bool] | None)], Any] | None


def string(val: list[int] | list[bool] | None) -> str:
    return ModbusClientMixin.convert_from_registers(registers=val, data_type=ModbusClientMixin.DATATYPE.STRING, word_order="big", string_encoding="ascii")

def integer(val: list[int] | list[bool] | None, type: ModbusClientMixin.DATATYPE) -> int:
    return ModbusClientMixin.convert_from_registers(registers=val, data_type=type, word_order="big")

def float32(val: list[int] | list[bool] | None) -> float:
    return ModbusClientMixin.convert_from_registers(registers=val, data_type=ModbusClientMixin.DATATYPE.FLOAT32, word_order="big")

def boolean(val: list[int] | list[bool] | None) -> bool:
    data = ModbusClientMixin.convert_from_registers(registers=val, data_type=ModbusClientMixin.DATATYPE.UINT16, word_order="big")
    assert (data == 0) or (data == 1)
    return bool(data)

def current_source(val: list[int] | list[bool] | None) -> CurrentLimitSource | str:
    data = ModbusClientMixin.convert_from_registers(registers=val, data_type=ModbusClientMixin.DATATYPE.UINT16, word_order="big")
    try:
        return CurrentLimitSource(data)
    except ValueError:
        return f"Unknown({data})"

def cp_state(val: list[int] | list[bool] | None) -> str:
    """Decode CpState: stored as ASCII char in a uint16 register."""
    data = ModbusClientMixin.convert_from_registers(registers=val, data_type=ModbusClientMixin.DATATYPE.UINT16, word_order="big")
    return chr(data) if data else "U"


def encode_uint32(val: int) -> list[int]:
    raw = int(val).to_bytes(4, "big")
    return [(raw[0] << 8) | raw[1], (raw[2] << 8) | raw[3]]

def encode_int32(val: int) -> list[int]:
    raw = int(val).to_bytes(4, "big", signed=True)
    return [(raw[0] << 8) | raw[1], (raw[2] << 8) | raw[3]]

def encode_uint16(val: int) -> list[int]:
    return [int(val) & 0xFFFF]


class ModbusAddresses(Enum):
    sEnergyTotalAddress = ModbusAddress(30_000, 4, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT64))
    sSessionEnergyAddress = ModbusAddress(30_004, 4, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT64))
    sPowerPhase1Address = ModbusAddress(30_008, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sPowerPhase2Address = ModbusAddress(30_010, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sPowerPhase3Address = ModbusAddress(30_012, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sPowerTotalAddress = ModbusAddress(30_014, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sVoltagePhase1Address = ModbusAddress(30_016, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sVoltagePhase2Address = ModbusAddress(30_018, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sVoltagePhase3Address = ModbusAddress(30_020, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sCurrentPhase1Address = ModbusAddress(30_022, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sCurrentPhase2Address = ModbusAddress(30_024, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sCurrentPhase3Address = ModbusAddress(30_026, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))

    # Config addresses
    sSerialNumberAddress = ModbusAddress(30_050, 12, None, partial(string))
    sProductNumberAddress = ModbusAddress(30_062, 12, None, partial(string))
    sFwIdentifierAddress = ModbusAddress(30_074, 12, None, partial(string))
    sHwIdentifierAddress = ModbusAddress(30_122, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sPhaseCountAddress = ModbusAddress(30_092, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sIndepRelayAddress = ModbusAddress(30_093, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))

    # CurrentControl addresses (read)
    sCurrentLimitSourceAddress = ModbusAddress(30_112, 1, None, current_source)
    sCurrentLimitActualAddress = ModbusAddress(30_113, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT32))

    # Holding registers (read + write)
    sModbusCurrentLimitAddress = ModbusAddress(40_000, 2, encode_uint32, partial(integer, type=ModbusClientMixin.DATATYPE.UINT32))
    sForce1PhaseAddress = ModbusAddress(40_002, 1, encode_uint16, boolean)
    sAliveTimeoutAddress = ModbusAddress(40_050, 2, encode_uint32, partial(integer, type=ModbusClientMixin.DATATYPE.UINT32))
    sFallbackCurrentAddress = ModbusAddress(40_052, 2, encode_int32, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))

    # Diagnostic addresses
    sWlanSignalStrenthAddress = ModbusAddress(30_086, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sCellSignalStrenthAddress = ModbusAddress(30_088, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.INT32))
    sUptimeAddress = ModbusAddress(30_090, 2, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT32))
    sCpStateAddress = ModbusAddress(30_110, 1, None, cp_state)
    sLockStateAddress = ModbusAddress(30_111, 1, None, boolean)

    sActiveWarning1Address = ModbusAddress(30_100, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sActiveWarning2Address = ModbusAddress(30_101, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sActiveWarning3Address = ModbusAddress(30_102, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sActiveWarning4Address = ModbusAddress(30_103, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sActiveWarning5Address = ModbusAddress(30_104, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))

    sActiveError1Address = ModbusAddress(30_105, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sActiveError2Address = ModbusAddress(30_106, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sActiveError3Address = ModbusAddress(30_107, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sActiveError4Address = ModbusAddress(30_108, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sActiveError5Address = ModbusAddress(30_109, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))

    sModbusApiVersionMajor = ModbusAddress(30_123, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
    sModbusApiVersionMinor = ModbusAddress(30_124, 1, None, partial(integer, type=ModbusClientMixin.DATATYPE.UINT16))
