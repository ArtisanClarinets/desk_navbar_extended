"""API module for Desk Navbar Extended - exposes main functions."""

import sys
from pathlib import Path

# Ensure parent can be imported
parent_path = str(Path(__file__).parent.parent)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

# Import main API functions from parent api.py module
# We need to reference it explicitly since we're shadowing it
import importlib.util

api_module_path = Path(__file__).parent.parent / "api.py"
spec = importlib.util.spec_from_file_location("main_api", api_module_path)
main_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_api)

# Re-export main API functions for backward compatibility
get_settings = main_api.get_settings
get_timezone_overview = main_api.get_timezone_overview
transcribe_audio = main_api.transcribe_audio
process_transcription = main_api.process_transcription
log_search_metrics = main_api.log_search_metrics

# Sub-modules available for import
from desk_navbar_extended.api import (  # noqa: F401, E402
    command_palette,
    help,
    history,
    kpi,
    notifications,
    pins,
    quick_create,
    saved_searches,
    search_filters,
)

__all__ = [
    # Main API functions
    "get_settings",
    "get_timezone_overview",
    "transcribe_audio",
    "process_transcription",
    "log_search_metrics",
    # Sub-modules
    "search_filters",
    "saved_searches",
    "pins",
    "quick_create",
    "command_palette",
    "history",
    "notifications",
    "kpi",
    "help",
]
