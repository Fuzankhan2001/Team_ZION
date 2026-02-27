BROKER = "localhost"
MQTT_PORT = 1883

DB_PARAMS = {
    "dbname": "hospitaldb",
    "user": "postgres",
    "password": "posthack",
    "host": "localhost",
    "port": 5432
}

# LLM Configuration
LLM_MODEL = "gpt-4o-mini"
LLM_TIMEOUT = 10

CHECK_INTERVAL_SECONDS = 15

# Risk Thresholds
BED_THRESHOLD = 0.8
VENT_THRESHOLD = 0.8
OXYGEN_CRITICAL = 30

# Referral Scoring Weights
DISTANCE_WEIGHT = 1.5
NO_BEDS_PENALTY = 40
NO_VENTS_PENALTY = 50
HIGH_BED_PENALTY = 15
HIGH_VENT_PENALTY = 20
LOW_OXYGEN_PENALTY = 30