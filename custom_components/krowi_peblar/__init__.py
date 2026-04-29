"""Krowi Peblar EV Charger integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    CONF_INTERVAL_HIGH,
    CONF_INTERVAL_MEDIUM,
    CONF_INTERVAL_LOW,
    CONF_INTERVAL_VERY_LOW,
    DEFAULT_PORT,
    DEFAULT_INTERVAL_HIGH,
    DEFAULT_INTERVAL_MEDIUM,
    DEFAULT_INTERVAL_LOW,
    DEFAULT_INTERVAL_VERY_LOW,
    DOMAIN,
    PLATFORMS,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
    PRIORITY_VERY_LOW,
)
from .coordinator import KrowiPeblarCoordinator
from .peblar_modbusclient.registers import ModbusAddresses

# ── Register lists per poll priority ─────────────────────────────────────────

_HIGH_REGISTERS = [
    ModbusAddresses.sPowerPhase1Address,
    ModbusAddresses.sPowerPhase2Address,
    ModbusAddresses.sPowerPhase3Address,
    ModbusAddresses.sPowerTotalAddress,
    ModbusAddresses.sVoltagePhase1Address,
    ModbusAddresses.sVoltagePhase2Address,
    ModbusAddresses.sVoltagePhase3Address,
    ModbusAddresses.sCurrentPhase1Address,
    ModbusAddresses.sCurrentPhase2Address,
    ModbusAddresses.sCurrentPhase3Address,
    ModbusAddresses.sCurrentLimitSourceAddress,
    ModbusAddresses.sCurrentLimitActualAddress,
    ModbusAddresses.sCpStateAddress,
    ModbusAddresses.sLockStateAddress,
]

_MEDIUM_REGISTERS = [
    ModbusAddresses.sEnergyTotalAddress,
    ModbusAddresses.sSessionEnergyAddress,
    ModbusAddresses.sModbusCurrentLimitAddress,
    ModbusAddresses.sForce1PhaseAddress,
    ModbusAddresses.sAliveTimeoutAddress,
    ModbusAddresses.sFallbackCurrentAddress,
]

_LOW_REGISTERS = [
    ModbusAddresses.sWlanSignalStrenthAddress,
    ModbusAddresses.sCellSignalStrenthAddress,
    ModbusAddresses.sUptimeAddress,
    ModbusAddresses.sActiveWarning1Address,
    ModbusAddresses.sActiveWarning2Address,
    ModbusAddresses.sActiveWarning3Address,
    ModbusAddresses.sActiveWarning4Address,
    ModbusAddresses.sActiveWarning5Address,
    ModbusAddresses.sActiveError1Address,
    ModbusAddresses.sActiveError2Address,
    ModbusAddresses.sActiveError3Address,
    ModbusAddresses.sActiveError4Address,
    ModbusAddresses.sActiveError5Address,
]

_VERY_LOW_REGISTERS = [
    ModbusAddresses.sSerialNumberAddress,
    ModbusAddresses.sProductNumberAddress,
    ModbusAddresses.sFwIdentifierAddress,
    ModbusAddresses.sHwIdentifierAddress,
    ModbusAddresses.sPhaseCountAddress,
    ModbusAddresses.sIndepRelayAddress,
    ModbusAddresses.sModbusApiVersionMajor,
    ModbusAddresses.sModbusApiVersionMinor,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Krowi Peblar from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    coordinators = {
        PRIORITY_HIGH: KrowiPeblarCoordinator(
            hass, host, port,
            entry.data.get(CONF_INTERVAL_HIGH, DEFAULT_INTERVAL_HIGH),
            _HIGH_REGISTERS, PRIORITY_HIGH,
        ),
        PRIORITY_MEDIUM: KrowiPeblarCoordinator(
            hass, host, port,
            entry.data.get(CONF_INTERVAL_MEDIUM, DEFAULT_INTERVAL_MEDIUM),
            _MEDIUM_REGISTERS, PRIORITY_MEDIUM,
        ),
        PRIORITY_LOW: KrowiPeblarCoordinator(
            hass, host, port,
            entry.data.get(CONF_INTERVAL_LOW, DEFAULT_INTERVAL_LOW),
            _LOW_REGISTERS, PRIORITY_LOW,
        ),
        PRIORITY_VERY_LOW: KrowiPeblarCoordinator(
            hass, host, port,
            entry.data.get(CONF_INTERVAL_VERY_LOW, DEFAULT_INTERVAL_VERY_LOW),
            _VERY_LOW_REGISTERS, PRIORITY_VERY_LOW,
        ),
    }

    for coordinator in coordinators.values():
        await coordinator.async_config_entry_first_refresh()

    # Build DeviceInfo once from static (very_low) coordinator data
    vl_data = coordinators[PRIORITY_VERY_LOW].data or {}
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Peblar EV Charger",
        manufacturer="Peblar",
        model=vl_data.get("sProductNumberAddress"),
        sw_version=vl_data.get("sFwIdentifierAddress"),
        serial_number=vl_data.get("sSerialNumberAddress"),
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        **coordinators,
        "device_info": device_info,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
