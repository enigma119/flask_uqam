volunteer_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "availability": {"type": "string"},
        "motivation": {"type": "string"},
    },
    "required": ["name", "email", "phone", "availability"],
}
