from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
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
            if obj["objectType"] == "Binary Input":
                entities.append(MyBinaryDeviceSensor(coordinator, sn, obj))
            else:
                entities.append(MyAnalogDeviceSensor(coordinator, sn, obj))

    async_add_entities(entities)

def analogInputTypeMapping(inputType):
    enumMap = {
        "Battery Voltage": (SensorDeviceClass.BATTERY, "%"),
        "Sensor Signal": (SensorDeviceClass.SIGNAL_STRENGTH, "dBm"),
        "Temperature": (SensorDeviceClass.TEMPERATURE, "°F"),
        "Diff Pressure": (SensorDeviceClass.PRESSURE, "Pa"),
        "Humidity": (SensorDeviceClass.HUMIDITY, "%"),
        "Light Level": (SensorDeviceClass.ILLUMINANCE, "lx"),
        "Bar Pressure": (SensorDeviceClass.ATMOSPHERIC_PRESSURE, "inHg"),
        "CO2": (SensorDeviceClass.CO2, "ppm"),
        "VOC": (SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, "ppb"),
        "NO2": (SensorDeviceClass.NITROGEN_DIOXIDE, "ppm"),
        "CO": (SensorDeviceClass.CO, "ppm"),
        "Refrigerant": (None, None),
        "Setpoint": (None, "%"),
        "CO2 Equivalent": (SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, "ppm"),
        "Particulate": (SensorDeviceClass.PM25, "µg/m³"),
    }

    return enumMap.get(inputType, (None, None))

def binaryInputTypeMapping(inputType):
    enumMap = {
        "Water Leak": BinarySensorDeviceClass.PROBLEM,
        "Motion": BinarySensorDeviceClass.MOTION,
        "Contact": BinarySensorDeviceClass.CONNECTIVITY,
    }

    return enumMap.get(inputType, None)

def voltage_to_pct_piecewise(v: float) -> float:
    """
    A more realistic (but still approximate) piecewise mapping.
    Adjust breakpoints for your battery / load curve.
    """
    # define breakpoints (voltage values) and their corresponding %’s
    # these are illustrative and need calibration
    breakpoints = [
        (3.6, 100),
        (3.4, 90),
        (3.2, 80),
        (3.0, 60),
        (2.8, 40),
        (2.5, 20),
        (2.2, 5),
        (2.0, 0),
    ]
    # if above highest
    if v >= breakpoints[0][0]:
        return 100.0
    # if below lowest
    if v <= breakpoints[-1][0]:
        return 0.0
    # find interval
    for i in range(len(breakpoints)-1):
        v_hi, pct_hi = breakpoints[i]
        v_lo, pct_lo = breakpoints[i+1]
        if v_hi >= v >= v_lo:
            # linear interp inside interval
            return pct_lo + (pct_hi - pct_lo) * (v - v_lo) / (v_hi - v_lo)
    # fallback
    return 0.0

class MyAnalogDeviceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, serial_number, obj):
        super().__init__(coordinator)
        self._serial = serial_number
        self._obj_id = obj["id"]
        self._name = obj.get("objectName", f"Object {self._obj_id}")
        self._unique_id = f"{serial_number}_{self._obj_id}"
        self._input_type = obj.get("inputType", None)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def native_unit_of_measurement(self):
        dev_class, unit = analogInputTypeMapping(self._input_type)
        return unit

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._serial)},
            "name": f"Device {self._serial}",
            "manufacturer": "BAPI",
        }

    @property
    def native_value(self):
        for obj in self.coordinator.data:
            if obj["id"] == self._obj_id:
                try:
                    if self._input_type == "Battery Voltage":
                        return voltage_to_pct_piecewise(float(obj.get("sensorValueRaw", 0)))
                    else:
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

    @property
    def device_class(self):
        dev_class, unit = analogInputTypeMapping(self._input_type)
        return dev_class



class MyBinaryDeviceSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, serial_number, obj):
        super().__init__(coordinator)
        self._serial = serial_number
        self._obj_id = obj["id"]
        self._name = obj.get("objectName", f"Object {self._obj_id}")
        self._unique_id = f"{serial_number}_{self._obj_id}"
        self._input_type = obj.get("inputType", None)

    @property
    def available(self):
        for obj in self.coordinator.data:
            if obj["id"] == self._obj_id:
                return not obj.get("errored", False)
        return False

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._serial)},
            "name": f"Device {self._serial}",
            "manufacturer": "BAPI",
        }
        
    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def device_class(self):
        return binaryInputTypeMapping(self._input_type)

    @property
    def is_on(self):
        for obj in self.coordinator.data:
            if obj["id"] == self._obj_id:
                try:
                    return float(obj.get("sensorValueRaw", 0)) == 1.0
                except (ValueError, TypeError):
                    return None
        return None