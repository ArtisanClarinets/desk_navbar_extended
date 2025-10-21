"""Public API exports for Desk Navbar Extended."""

from desk_navbar_extended import root_api as _root_api

get_settings = _root_api.get_settings
get_timezone_overview = _root_api.get_timezone_overview
transcribe_audio = _root_api.transcribe_audio
process_transcription = _root_api.process_transcription
log_search_metrics = _root_api.log_search_metrics
log_doctype_presence = _root_api.log_doctype_presence

from . import (  # noqa: F401
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
    "get_settings",
    "get_timezone_overview",
    "transcribe_audio",
    "process_transcription",
    "log_search_metrics",
    "log_doctype_presence",
    "command_palette",
    "help",
    "history",
    "kpi",
    "notifications",
    "pins",
    "quick_create",
    "saved_searches",
    "search_filters",
]
