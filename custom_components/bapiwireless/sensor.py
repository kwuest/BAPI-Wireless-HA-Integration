from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Group by sensorSerialNumber
    sensors_by_device = {}
    for obj in coordinator.data:
        sn = obj["sensorSerialNumber"]
        sensors_by_device.setdefault(sn, []).append(obj)

    for sn, objs in sensors_by_device.items():
        for obj in objs:
            entities.append(MyDeviceSensor(coordinator, sn, obj))

    async_add_entities(entities)

class MyDeviceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, serial_number, obj):
        super().__init__(coordinator)
        self._serial = serial_number
        self._obj_id = obj["id"]
        self._name = obj.get("objectName", f"Object {self._obj_id}")
        self._unit = obj.get("unitType")
        self._unique_id = f"{serial_number}_{self._obj_id}"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._serial)},
            "name": f"Device {self._serial}",
            "manufacturer": "Custom Embedded Device",
        }

    @property
    def native_value(self):
        for obj in self.coordinator.data:
            if obj["id"] == self._obj_id:
                try:
                    return float(obj.get("sensorValueRaw", 0))
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def available(self):
        for obj in self.coordinator.data:
            if obj["id"] == self._obj_id:
                return not obj.get("errored", False)
        return False
