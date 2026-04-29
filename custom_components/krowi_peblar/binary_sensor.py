"""Binary sensor platform for the Krowi Peblar integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PRIORITY_HIGH, PRIORITY_MEDIUM
from .coordinator import KrowiPeblarCoordinator


@dataclass(frozen=True, kw_only=True)
class KrowiPeblarBinarySensorDescription(BinarySensorEntityDescription):
    register: str  # ModbusAddresses enum name


# ── High priority (5 s) — changes during charging session ────────────────────────
_HIGH_BINARY_SENSORS: tuple[KrowiPeblarBinarySensorDescription, ...] = (
    KrowiPeblarBinarySensorDescription(
        key="lock_state",
        register="sLockStateAddress",
        name="Lock State",
        device_class=BinarySensorDeviceClass.LOCK,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

# ── Medium priority (30 s) — configuration state ──────────────────────────────
_MEDIUM_BINARY_SENSORS: tuple[KrowiPeblarBinarySensorDescription, ...] = (
    KrowiPeblarBinarySensorDescription(
        key="force_1phase",
        register="sForce1PhaseAddress",
        name="Force 1-Phase",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

_PRIORITY_BINARY_SENSORS = [
    (PRIORITY_HIGH, _HIGH_BINARY_SENSORS),
    (PRIORITY_MEDIUM, _MEDIUM_BINARY_SENSORS),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    device_info: DeviceInfo = entry_data["device_info"]
    entities = []
    for priority, descriptions in _PRIORITY_BINARY_SENSORS:
        coordinator: KrowiPeblarCoordinator = entry_data[priority]
        entities.extend(
            KrowiPeblarBinarySensor(coordinator, entry, description, device_info)
            for description in descriptions
        )
    async_add_entities(entities)


class KrowiPeblarBinarySensor(
    CoordinatorEntity[KrowiPeblarCoordinator], BinarySensorEntity
):
    """A binary sensor reading a boolean Modbus register from the Peblar charger."""

    entity_description: KrowiPeblarBinarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KrowiPeblarCoordinator,
        entry: ConfigEntry,
        description: KrowiPeblarBinarySensorDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool | None:
        value = (self.coordinator.data or {}).get(self.entity_description.register)
        if value is None:
            return None
        return bool(value)
