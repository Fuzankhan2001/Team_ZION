# ============================================
# IoT Simulator Configuration
# Phase 3: Added simulation speed
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

# Speed multiplier — higher = faster simulation
SIMULATION_SPEED_FACTOR = 1.0
