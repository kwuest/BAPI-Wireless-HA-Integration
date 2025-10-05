# 🧩 My Device Sensors (Home Assistant Integration)

A custom [Home Assistant](https://www.home-assistant.io) integration that connects BAPI Wireless products into Home Assistant and automatically imports all sensor data from its REST API endpoints.

---

## 🚀 Features

✅ Auto-discovers all available sensors from your wireless system  
✅ Groups entities by their `Serial Number` (one device per sensor)  
✅ Supports adjustable polling interval (via UI options)  
✅ Fully configurable via Home Assistant UI (no YAML needed)  
✅ Works entirely over local network — no cloud required

``` 

Each unique `sensorSerialNumber` becomes a **device**, and each object becomes a **sensor entity**.

---

## 🧠 Example in Home Assistant

**Device:**  
`Sensor A1B2C3D4E5F6`

**Entities:**  
- Zone 1 Temperature → 23.4 °C  
- Zone 1 Humidity → 42.3 %  
- Zone 1 CO₂ → 856 ppm  

---

## 🧩 Installation via HACS

### Option 1 — Add as a Custom Repository

1. Go to **HACS → Integrations → ⋮ (three dots) → Custom Repositories**  
2. Add        and select **Integration** as the category.  
3. Click **Add → Download → Install**.  
4. Restart Home Assistant.

---

### Option 2 — Manual Installation

1. Copy the folder `custom_components/BAPIWireless/` into your Home Assistant `config/custom_components/` directory.  
2. Restart Home Assistant.

---

## ⚙️ Setup Instructions

1. In Home Assistant, go to **Settings → Devices & Services → + Add Integration**.  
2. Search for **BAPI Wireless**.  
3. Enter:
- **Base URL** → e.g. `http://192.168.1.50`
- **Polling Interval** → in seconds (default 30)
4. Click **Submit**.

After setup, Home Assistant will automatically discover all devices and entities.

---

## 🧭 Configuration Options

You can change the polling interval later:

1. Go to **Settings → Devices & Services → My Device Sensors → Configure**  
2. Adjust the polling interval (seconds).  
3. Click **Submit**.

---

## 🧰 File Structure

custom_components/BAPIWireless/
├── __init__.py
├── manifest.json
├── sensor.py
├── const.py
├── config_flow.py
└── translations/
 └── en.json
hacs.json



---

## 📦 Requirements

- Home Assistant 2025.7.4 or later  

---

## 🧑‍💻 Developer Info

- **Domain:** `BAPIWireless`  
- **IoT Class:** Local Polling  
- **Language:** Python 3.12 (Home Assistant core runtime)

---

## 🪛 Troubleshooting

If no sensors appear:
1. Confirm you can access your device’s `/Objects` endpoint in a browser.  
2. Check **Settings → System → Logs** in Home Assistant for any “cannot connect” or JSON errors.  

---

## 📄 License

MIT License © 2025 [Your Name or Organization]

