import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_BASE_URL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

async def validate_input(hass: HomeAssistant, data):
    """Check that the device URL is reachable."""
    session = async_get_clientsession(hass)
    async with session.get(f"{data[CONF_BASE_URL]}/Objects") as resp:
        if resp.status != 200:
            raise ValueError("Device not reachable")
    return True

class MyDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                return self.async_create_entry(title="My Device", data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required(CONF_BASE_URL): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, import_config):
        return await self.async_step_user(import_config)

class MyDeviceOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ): int,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
