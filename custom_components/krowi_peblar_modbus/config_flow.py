"""Config flow for the Krowi Peblar integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    CONF_INTERVAL_HIGH,
    CONF_INTERVAL_MEDIUM,
    CONF_INTERVAL_LOW,
    CONF_INTERVAL_VERY_LOW,
    DEFAULT_INTERVAL_HIGH,
    DEFAULT_INTERVAL_MEDIUM,
    DEFAULT_INTERVAL_LOW,
    DEFAULT_INTERVAL_VERY_LOW,
)


class KrowiPeblarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Krowi Peblar Modbus."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = int(user_input[CONF_PORT])

            # Prevent duplicate entries for the same host:port
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            try:
                await self._validate_connection(host, port)
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Peblar ({host})",
                    data={**user_input, CONF_PORT: port},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(CONF_PORT, default=DEFAULT_PORT): NumberSelector(
                    NumberSelectorConfig(min=1, max=65535, step=1, mode=NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_INTERVAL_HIGH, default=DEFAULT_INTERVAL_HIGH): NumberSelector(
                    NumberSelectorConfig(min=1, max=60, step=1, mode=NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_INTERVAL_MEDIUM, default=DEFAULT_INTERVAL_MEDIUM): NumberSelector(
                    NumberSelectorConfig(min=5, max=3600, step=1, mode=NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_INTERVAL_LOW, default=DEFAULT_INTERVAL_LOW): NumberSelector(
                    NumberSelectorConfig(min=5, max=3600, step=1, mode=NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_INTERVAL_VERY_LOW, default=DEFAULT_INTERVAL_VERY_LOW): NumberSelector(
                    NumberSelectorConfig(min=10, max=3600, step=1, mode=NumberSelectorMode.BOX)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _validate_connection(self, host: str, port: int) -> None:
        """Try to read the serial number register to validate connectivity."""
        from .peblar_modbusclient.modbus import Modbus
        from .peblar_modbusclient.registers import ModbusAddresses

        def _test() -> None:
            modbus = Modbus(host, port)
            modbus.read(ModbusAddresses.sSerialNumberAddress.value)

        await self.hass.async_add_executor_job(_test)
