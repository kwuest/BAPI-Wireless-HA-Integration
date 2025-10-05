import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_BASE_URL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    base_url = entry.data[CONF_BASE_URL]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    session = async_get_clientsession(hass)

    async def async_update_data():
        try:
            async with session.get(f"{base_url}/Objects") as resp:
                ids = await resp.json(content_type=None)
            objects = []
            for oid in ids:
                async with session.get(f"{base_url}/Object/{oid}") as resp:
                    obj = await resp.json(content_type=None)
                    objects.append(obj)
            return objects
        except Exception as e:
            raise UpdateFailed(f"Failed to fetch data: {e}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="my_device_data",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def _update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
