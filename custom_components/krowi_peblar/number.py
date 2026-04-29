"""Number platform for the Krowi Peblar integration (writable Modbus registers)."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PRIORITY_MEDIUM
from .coordinator import KrowiPeblarCoordinator
from .peblar_modbusclient.registers import ModbusAddresses


@dataclass(frozen=True, kw_only=True)
class KrowiPeblarNumberDescription(NumberEntityDescription):
    register: ModbusAddresses


# All writable holding registers are polled at medium priority
NUMBER_DESCRIPTIONS: tuple[KrowiPeblarNumberDescription, ...] = (
    KrowiPeblarNumberDescription(
        key="modbus_current_limit",
        register=ModbusAddresses.sModbusCurrentLimitAddress,
        name="Modbus Current Limit",
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLI_AMPERE,
        native_min_value=0,
        native_max_value=32000,
        native_step=1000,
        mode=NumberMode.BOX,
    ),
    KrowiPeblarNumberDescription(
        key="alive_timeout",
        register=ModbusAddresses.sAliveTimeoutAddress,
        name="Alive Timeout",
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=3600,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    KrowiPeblarNumberDescription(
        key="fallback_current",
        register=ModbusAddresses.sFallbackCurrentAddress,
        name="Fallback Current",
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLI_AMPERE,
        native_min_value=0,
        native_max_value=32000,
        native_step=1000,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KrowiPeblarCoordinator = entry_data[PRIORITY_MEDIUM]
    device_info: DeviceInfo = entry_data["device_info"]
    async_add_entities(
        KrowiPeblarNumber(coordinator, entry, description, device_info)
        for description in NUMBER_DESCRIPTIONS
    )


class KrowiPeblarNumber(CoordinatorEntity[KrowiPeblarCoordinator], NumberEntity):
    """A number entity backed by a writable Modbus holding register."""

    entity_description: KrowiPeblarNumberDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KrowiPeblarCoordinator,
        entry: ConfigEntry,
        description: KrowiPeblarNumberDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> float | None:
        value = (self.coordinator.data or {}).get(
            self.entity_description.register.name
        )
        if value is None:
            return None
        return float(value)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_register(
            self.entity_description.register, int(value)
        )
