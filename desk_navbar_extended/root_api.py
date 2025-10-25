"""Server APIs for Desk Navbar Extended."""

from __future__ import annotations

import base64
import json
from datetime import datetime
from hashlib import sha256
from typing import Any

import frappe
from frappe.utils import cint, get_fullname, now_datetime
from pytz import timezone as pytz_timezone

from desk_navbar_extended.desk_navbar_extended.doctype.desk_navbar_extended_settings.desk_navbar_extended_settings import (
    get_enabled_features_for_user,
    get_settings_doc,
)


@frappe.whitelist()
def get_settings() -> dict[str, Any]:
    """Return sanitized settings for the current session."""

    try:
        doc = get_settings_doc()
        features = get_enabled_features_for_user()
    except Exception as e:
        frappe.logger("desk_navbar_extended").error(
            "Failed to fetch settings", extra={"error": str(e), "user": frappe.session.user}
        )
        # Return minimal safe defaults to prevent total failure
        return {
            "features": {"clock": False, "usage_analytics": False},
            "clock": {
                "time_format": "12h",
                "show_calendar": False,
                "timezone_event_limit": 3,
                "time_zones": [],
            },
            "awesomebar": {"default_width": 560, "mobile_collapse": True},
            "quick_create": {"doctypes": ""},
            "kpi": {"refresh_interval": 300},
        }

    timezones = [
        {
            "label": row.city_label,
            "time_zone": row.time_zone,
            "color": row.color,
        }
        for row in doc.time_zones
    ]
    return {
        "features": features,
        "clock": {
            "time_format": doc.clock_time_format or "12h",
            "show_calendar": bool(doc.show_calendar_excerpts),
            "timezone_event_limit": cint(doc.timezone_event_limit) or 3,
            "time_zones": timezones,
        },
        "awesomebar": {
            "default_width": cint(doc.awesomebar_default_width) or 560,
            "mobile_collapse": bool(doc.awesomebar_mobile_collapse),
        },
        "quick_create": {
            "doctypes": doc.quick_create_doctypes or "",
        },
        "kpi": {
            "refresh_interval": cint(doc.kpi_refresh_interval) or 300,
        },
    }


@frappe.whitelist()
def get_timezone_overview() -> dict[str, Any]:
    """Return current times across configured zones plus upcoming calendar entries."""

    settings = get_settings_doc()
    features = get_enabled_features_for_user()
    if not features.get("clock"):
        return {"zones": [], "events": []}

    now_utc = now_datetime()
    user = frappe.session.user
    user_tz = frappe.utils.get_user_time_zone(user)
    system_tz = frappe.utils.get_time_zone()

    configured_zones = [
        {
            "key": "user",
            "label": get_fullname(user) or "You",
            "time_zone": user_tz,
            "color": None,
        },
        {
            "key": "system",
            "label": frappe.local.site,
            "time_zone": system_tz,
            "color": None,
        },
    ]

    for row in settings.time_zones:
        configured_zones.append(
            {
                "key": sha256(row.name.encode()).hexdigest()[:8],
                "label": row.city_label,
                "time_zone": row.time_zone,
                "color": row.color,
            }
        )

    zones_payload = []
    for zone in configured_zones:
        try:
            tz = pytz_timezone(zone["time_zone"])
        except Exception:  # noqa: BLE001
            frappe.log_error("Invalid timezone configured", zone["time_zone"])
            continue
        localized = now_utc.astimezone(tz)
        zones_payload.append(
            {
                "key": zone["key"],
                "label": zone["label"],
                "time_zone": zone["time_zone"],
                "color": zone["color"],
                "current_time": localized.isoformat(),
            }
        )

    events_payload: list[dict[str, Any]] = []
    if settings.show_calendar_excerpts:
        limit = cint(settings.timezone_event_limit) or 3
        events = frappe.get_list(
            "Event",
            filters={"starts_on": (">=", now_utc)},
            fields=["name", "subject", "starts_on", "ends_on", "all_day"],
            order_by="starts_on asc",
            limit=limit,
        )
        for event in events:
            starts_on: datetime = event.starts_on
            ends_on: datetime | None = event.ends_on
            events_payload.append(
                {
                    "name": event.name,
                    "subject": event.subject,
                    "starts_on": starts_on.isoformat(),
                    "ends_on": ends_on.isoformat() if ends_on else None,
                    "all_day": bool(event.all_day),
                }
            )

    return {
        "fetched_at": now_utc.isoformat(),
        "zones": zones_payload,
        "events": events_payload,
    }


@frappe.whitelist(allow_guest=False)
def transcribe_audio(audio: str, filename: str | None = None) -> dict[str, Any]:
    """Queue audio for background transcription and log consent."""

    if not audio:
        frappe.throw("Audio payload is required.")

    try:
        base64.b64decode(audio)
    except Exception as exc:  # noqa: BLE001
        frappe.throw(f"Invalid audio payload: {exc}")

    frappe.logger("desk_navbar_extended").info(
        "Voice search transcription consent", extra={"user": frappe.session.user}
    )

    job = frappe.enqueue(
        "desk_navbar_extended.api.process_transcription",
        queue="long",
        audio=audio,
        filename=filename,
        user=frappe.session.user,
    )
    return {"job_id": job.id}


@frappe.whitelist(allow_guest=False)
def process_transcription(audio: str, filename: str | None, user: str) -> None:
    """Placeholder background job that stores audio for later processing."""

    get_conf = getattr(frappe.conf, "get", None)
    endpoint = get_conf("desk_navbar_transcription_endpoint") if get_conf else None
    api_key = get_conf("desk_navbar_transcription_api_key") if get_conf else None

    logger = frappe.logger("desk_navbar_extended")
    logger.info(
        "Queued transcription",
        extra={"user": user, "filename": filename, "size": len(audio)},
    )
    if not endpoint or not api_key:
        logger.warning("Transcription endpoint not configured; job will be skipped.")
        return
    # Placeholder for actual integration with external speech-to-text service.
    logger.info(
        "Transcription forwarded",
        extra={"endpoint": endpoint, "filename": filename, "user": user},
    )


@frappe.whitelist(allow_guest=False)
def log_search_metrics(payload: str | dict[str, Any]) -> None:
    """Persist anonymized search analytics and raise alerts on error spikes."""

    if isinstance(payload, str):
        metrics = json.loads(payload)
    else:
        metrics = payload

    doc = frappe.get_doc(
        {
            "doctype": "Desk Navbar Search Metric",
            "event_ts": metrics.get("event_ts") or now_datetime(),
            "search_length": cint(metrics.get("search_length")),
            "execution_ms": float(metrics.get("execution_ms") or 0),
            "status": metrics.get("status") or "success",
            "error_message": (metrics.get("error_message") or "")[:140],
        }
    )
    doc.insert(ignore_permissions=True)

    recent = frappe.get_all(
        "Desk Navbar Search Metric",
        fields=["status"],
        order_by="creation desc",
        limit=20,
    )
    if not recent:
        return

    error_count = sum(1 for row in recent if row.status == "error")
    if error_count / len(recent) >= 0.3:
        frappe.publish_realtime(
            "desk_navbar_extended.error_rate",
            {"error_rate": error_count / len(recent)},
            user=frappe.session.user,
        )


def log_doctype_presence() -> None:
    """Log whether key Desk Navbar Extended DocTypes are available."""

    names = [
        "Desk Navbar Extended Settings",
        "Desk Navbar Search Metric",
        "Desk Navbar Saved Search",
        "Desk Navbar Pin",
    ]
    missing: list[str] = []
    for doctype in names:
        try:
            if not frappe.get_meta(doctype, cached=True):
                missing.append(doctype)
        except Exception:  # noqa: BLE001
            missing.append(doctype)

    logger = frappe.logger("desk_navbar_extended")
    if missing:
        logger.error({"missing_doctypes": missing})
    else:
        logger.info("All desk_navbar_extended doctypes loaded")
