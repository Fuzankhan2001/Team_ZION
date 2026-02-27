# ============================================
# IoT Simulator Configuration
# Phase 2: Per-hospital configs
# ============================================

BROKER = "localhost"
MQTT_PORT = 1883

FACILITIES = ["H001", "H002", "H003", "H004"]

HOSPITAL_CONFIGS = {
    "H001": {"beds": 10, "ventilators": 10, "oxygen_cylinders": 4},
    "H002": {"beds": 10, "ventilators": 10, "oxygen_cylinders": 4},
    "H003": {"beds": 10, "ventilators": 10, "oxygen_cylinders": 4},
    "H004": {"beds": 10, "ventilators": 10, "oxygen_cylinders": 4},
}
