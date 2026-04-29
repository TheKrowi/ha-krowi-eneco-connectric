"""Constants for the Krowi Peblar integration."""

DOMAIN = "krowi_peblar"
DEFAULT_PORT = 502

PLATFORMS = ["sensor", "binary_sensor", "number"]

# Config entry keys for poll intervals
CONF_INTERVAL_HIGH = "interval_high"
CONF_INTERVAL_MEDIUM = "interval_medium"
CONF_INTERVAL_LOW = "interval_low"
CONF_INTERVAL_VERY_LOW = "interval_very_low"

# Default poll intervals (seconds)
DEFAULT_INTERVAL_HIGH = 5
DEFAULT_INTERVAL_MEDIUM = 30
DEFAULT_INTERVAL_LOW = 60
DEFAULT_INTERVAL_VERY_LOW = 300

# Priority keys (also used as coordinator dict keys in hass.data)
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"
PRIORITY_VERY_LOW = "very_low"
