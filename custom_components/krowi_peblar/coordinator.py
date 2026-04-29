"""DataUpdateCoordinator for the Krowi Peblar integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .peblar_modbusclient.modbus import Modbus
from .peblar_modbusclient.registers import ModbusAddresses  # used by async_write_register callers

_LOGGER = logging.getLogger(__name__)


class KrowiPeblarCoordinator(DataUpdateCoordinator[dict]):
    """Polls all readable Modbus registers from a Peblar EV charger."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        scan_interval: int,
        registers: list,
        priority: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{priority}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.host = host
        self.port = port
        self._registers = registers
        self._modbus = Modbus(host, port)

    # ------------------------------------------------------------------
    # Private helpers (run in executor – blocking Modbus calls)
    # ------------------------------------------------------------------

    def _fetch_all(self) -> dict:
        """Read assigned registers; store None on failure."""
        data: dict = {}
        for address in self._registers:
            try:
                data[address.name] = self._modbus.read(address.value)
            except Exception:  # noqa: BLE001
                data[address.name] = None
        return data

    def _do_write(self, address: ModbusAddresses, value) -> None:
        self._modbus.write(address.value, value)

    # ------------------------------------------------------------------
    # DataUpdateCoordinator interface
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(self._fetch_all)
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with Peblar charger at {self.host}: {err}"
            ) from err

    async def async_write_register(
        self, address: ModbusAddresses, value
    ) -> None:
        """Write a value to a holding register and refresh coordinator data."""
        await self.hass.async_add_executor_job(self._do_write, address, value)
        await self.async_request_refresh()
