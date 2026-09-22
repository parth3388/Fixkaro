"""The canonical service catalog.

These slugs/names are seeded into the `services` table by the initial Alembic
migration. The `name` values are copied verbatim from the <option> text in
index.html and contact.html's #category select, so that
find_service_by_name_or_slug() matches what the existing frontend already
sends without any HTML changes. See BACKEND_ASSUMPTIONS.md.
"""

SERVICES: list[dict[str, str]] = [
    {
        "slug": "ac-cooling",
        "name": "AC & Cooling",
        "description": "Inspection, servicing, deep cleaning and repair support.",
    },
    {
        "slug": "washing-machine",
        "name": "Washing Machine",
        "description": "Diagnosis and repair for common washing and drainage issues.",
    },
    {
        "slug": "refrigerator",
        "name": "Refrigerator",
        "description": "Cooling, thermostat, gas and general repair assistance.",
    },
    {
        "slug": "television",
        "name": "Television",
        "description": "Display, sound, power and connectivity troubleshooting.",
    },
    {
        "slug": "geyser",
        "name": "Geyser",
        "description": "Heating, leakage, installation and safety inspection.",
    },
    {
        "slug": "water-purifier",
        "name": "Water Purifier",
        "description": "Filter service, maintenance and purification-system repair.",
    },
    {
        "slug": "pc-laptop",
        "name": "PC & Laptop",
        "description": "Diagnostics, setup, upgrades and technical support.",
    },
    {
        "slug": "cctv-networking",
        "name": "CCTV & Networking",
        "description": "Installation, configuration and connectivity assistance.",
    },
    {
        "slug": "business-institutional",
        "name": "Business or Institutional",
        "description": "Structured appliance and technology support for organisations.",
    },
    {
        "slug": "other",
        "name": "Other",
        "description": "Not sure which category fits? Tell us the issue and we will route it.",
    },
]
