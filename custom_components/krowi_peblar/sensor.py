"""Sensor platform for the Krowi Peblar integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW, PRIORITY_VERY_LOW
from .coordinator import KrowiPeblarCoordinator
from .peblar_modbusclient.registers import CurrentLimitSource


@dataclass(frozen=True, kw_only=True)
class KrowiPeblarSensorDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with the register key."""
    register: str  # ModbusAddresses enum name


# ── High priority (5 s) — real-time measurements ─────────────────────────────────
_HIGH_SENSORS: tuple[KrowiPeblarSensorDescription, ...] = (
    KrowiPeblarSensorDescription(
        key="power_phase1",
        register="sPowerPhase1Address",
        name="Power Phase 1",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    KrowiPeblarSensorDescription(
        key="power_phase2",
        register="sPowerPhase2Address",
        name="Power Phase 2",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    KrowiPeblarSensorDescription(
        key="power_phase3",
        register="sPowerPhase3Address",
        name="Power Phase 3",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    KrowiPeblarSensorDescription(
        key="power_total",
        register="sPowerTotalAddress",
        name="Total Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    KrowiPeblarSensorDescription(
        key="voltage_phase1",
        register="sVoltagePhase1Address",
        name="Voltage Phase 1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    KrowiPeblarSensorDescription(
        key="voltage_phase2",
        register="sVoltagePhase2Address",
        name="Voltage Phase 2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    KrowiPeblarSensorDescription(
        key="voltage_phase3",
        register="sVoltagePhase3Address",
        name="Voltage Phase 3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    KrowiPeblarSensorDescription(
        key="current_phase1",
        register="sCurrentPhase1Address",
        name="Current Phase 1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
    ),
    KrowiPeblarSensorDescription(
        key="current_phase2",
        register="sCurrentPhase2Address",
        name="Current Phase 2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
    ),
    KrowiPeblarSensorDescription(
        key="current_phase3",
        register="sCurrentPhase3Address",
        name="Current Phase 3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
    ),
    KrowiPeblarSensorDescription(
        key="current_limit_source",
        register="sCurrentLimitSourceAddress",
        name="Current Limit Source",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KrowiPeblarSensorDescription(
        key="current_limit_actual",
        register="sCurrentLimitActualAddress",
        name="Current Limit Actual",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KrowiPeblarSensorDescription(
        key="cp_state",
        register="sCpStateAddress",
        name="CP State",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

# ── Medium priority (30 s) — session data ───────────────────────────────────────
_MEDIUM_SENSORS: tuple[KrowiPeblarSensorDescription, ...] = (
    KrowiPeblarSensorDescription(
        key="energy_total",
        register="sEnergyTotalAddress",
        name="Total Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    KrowiPeblarSensorDescription(
        key="session_energy",
        register="sSessionEnergyAddress",
        name="Session Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
)

# ── Low priority (60 s) — diagnostics ───────────────────────────────────────────
_LOW_SENSORS: tuple[KrowiPeblarSensorDescription, ...] = (
    KrowiPeblarSensorDescription(
        key="wlan_signal",
        register="sWlanSignalStrenthAddress",
        name="WLAN Signal Strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="cell_signal",
        register="sCellSignalStrenthAddress",
        name="Cell Signal Strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="uptime",
        register="sUptimeAddress",
        name="Uptime",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="warning_1",
        register="sActiveWarning1Address",
        name="Active Warning 1",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="warning_2",
        register="sActiveWarning2Address",
        name="Active Warning 2",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="warning_3",
        register="sActiveWarning3Address",
        name="Active Warning 3",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="warning_4",
        register="sActiveWarning4Address",
        name="Active Warning 4",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="warning_5",
        register="sActiveWarning5Address",
        name="Active Warning 5",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="error_1",
        register="sActiveError1Address",
        name="Active Error 1",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="error_2",
        register="sActiveError2Address",
        name="Active Error 2",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="error_3",
        register="sActiveError3Address",
        name="Active Error 3",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="error_4",
        register="sActiveError4Address",
        name="Active Error 4",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="error_5",
        register="sActiveError5Address",
        name="Active Error 5",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)

# ── Very low priority (300 s) — static device info ────────────────────────────
_VERY_LOW_SENSORS: tuple[KrowiPeblarSensorDescription, ...] = (
    KrowiPeblarSensorDescription(
        key="serial_number",
        register="sSerialNumberAddress",
        name="Serial Number",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="product_number",
        register="sProductNumberAddress",
        name="Product Number",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="fw_version",
        register="sFwIdentifierAddress",
        name="Firmware Version",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="hw_revision",
        register="sHwIdentifierAddress",
        name="Hardware Revision",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="phase_count",
        register="sPhaseCountAddress",
        name="Phase Count",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KrowiPeblarSensorDescription(
        key="modbus_api_major",
        register="sModbusApiVersionMajor",
        name="Modbus API Version Major",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    KrowiPeblarSensorDescription(
        key="modbus_api_minor",
        register="sModbusApiVersionMinor",
        name="Modbus API Version Minor",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)

_PRIORITY_SENSORS = [
    (PRIORITY_HIGH, _HIGH_SENSORS),
    (PRIORITY_MEDIUM, _MEDIUM_SENSORS),
    (PRIORITY_LOW, _LOW_SENSORS),
    (PRIORITY_VERY_LOW, _VERY_LOW_SENSORS),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    device_info: DeviceInfo = entry_data["device_info"]
    entities = []
    for priority, descriptions in _PRIORITY_SENSORS:
        coordinator: KrowiPeblarCoordinator = entry_data[priority]
        entities.extend(
            KrowiPeblarSensor(coordinator, entry, description, device_info)
            for description in descriptions
        )
    async_add_entities(entities)


class KrowiPeblarSensor(CoordinatorEntity[KrowiPeblarCoordinator], SensorEntity):
    """A sensor reading a single Modbus register from the Peblar charger."""

    entity_description: KrowiPeblarSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KrowiPeblarCoordinator,
        entry: ConfigEntry,
        description: KrowiPeblarSensorDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self):
        value = (self.coordinator.data or {}).get(
            self.entity_description.register
        )
        if value is None:
            return None
        # Convert enum to its name string for display
        if isinstance(value, CurrentLimitSource):
            return value.name
        return value
