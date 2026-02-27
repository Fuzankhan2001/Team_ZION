def classify_severity(severity_text: str) -> dict:
    """Classify severity into a structured format."""
    severity_map = {
        "CRITICAL": {"level": 1, "label": "Critical", "color": "red", "priority": "IMMEDIATE"},
        "SEVERE": {"level": 2, "label": "Severe", "color": "orange", "priority": "HIGH"},
        "MODERATE": {"level": 3, "label": "Moderate", "color": "yellow", "priority": "MEDIUM"},
        "MILD": {"level": 4, "label": "Mild", "color": "green", "priority": "LOW"},
    }

    severity_upper = severity_text.upper()
    return severity_map.get(severity_upper, {
        "level": 3,
        "label": severity_text,
        "color": "yellow",
        "priority": "MEDIUM"
    })
