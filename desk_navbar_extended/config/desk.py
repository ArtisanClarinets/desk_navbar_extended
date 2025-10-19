from __future__ import annotations


def get_data():
    return [
        {
            "module_name": "Desk Navbar Extended",
            "label": "Desk Navbar Extended",
            "color": "blue",
            "icon": "octicon octicon-clock",
            "type": "module",
            "items": [
                {
                    "type": "doctype",
                    "name": "Desk Navbar Search Metric",
                    "label": "Search Metrics",
                    "description": "Monitor awesomebar usage telemetry.",
                },
                {
                    "type": "link",
                    "label": "Configuration",
                    "link_type": "Form",
                    "link_to": "Desk Navbar Extended Settings",
                    "dependencies": ["Desk Navbar Extended Settings"],
                },
            ],
        }
    ]
