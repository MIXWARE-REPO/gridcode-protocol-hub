from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Any, Optional

import requests


@dataclass
class ChargerCredentials:
    ip: str
    username: str
    password: str


@dataclass
class EndpointChangeResult:
    before_endpoint: str
    target_endpoint: str
    after_endpoint: str
    saved: bool
    reason: str


def _base_url(ip: str) -> str:
    return f"http://{ip}"


def _extract_endpoint_from_html(html: str) -> str:
    patterns = [
        r'name=["\']centralSystemAddress["\']\s+[^>]*value=["\']([^"\']+)["\']',
        r'id=["\']centralSystemAddress["\']\s+[^>]*value=["\']([^"\']+)["\']',
        r'value=["\'](ws://[^"\']+)["\']',
        r'value=["\'](wss://[^"\']+)["\']',
    ]
    for p in patterns:
        m = re.search(p, html, re.I)
        if m:
            return m.group(1).strip()

    m = re.search(r'(ws://[^"\'\s<>]+|wss://[^"\'\s<>]+)', html, re.I)
    return m.group(1).strip() if m else ""


def login_session(creds: ChargerCredentials, timeout: int = 20) -> requests.Session:
    s = requests.Session()
    url = _base_url(creds.ip) + "/"
    s.get(url, timeout=timeout)
    s.post(
        url,
        data={"username": creds.username, "pass": creds.password, "button_login": "LOG IN"},
        timeout=timeout,
    )
    return s


def fetch_main_html(session: requests.Session, ip: str, timeout: int = 20) -> str:
    r = session.get(_base_url(ip) + "/index_main.php", timeout=timeout)
    r.raise_for_status()
    return r.text


def get_current_ocpp_endpoint(session: requests.Session, ip: str, timeout: int = 20) -> str:
    html = fetch_main_html(session, ip, timeout=timeout)
    return _extract_endpoint_from_html(html)


def _extract_all_form_fields(html: str) -> Dict[str, str]:
    payload: Dict[str, str] = {}

    for m in re.finditer(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', html, re.I):
        tag = m.group(0)
        name = m.group(1)
        vm = re.search(r'value=["\']([^"\']*)["\']', tag, re.I)
        payload[name] = vm.group(1) if vm else ""

    # select selected option
    for sm in re.finditer(r'<select[^>]*name=["\']([^"\']+)["\'][^>]*>(.*?)</select>', html, re.I | re.S):
        name, body = sm.group(1), sm.group(2)
        om = re.search(r'<option[^>]*selected[^>]*value=["\']([^"\']+)["\']', body, re.I)
        if not om:
            om = re.search(r'<option[^>]*value=["\']([^"\']+)["\']', body, re.I)
        if om:
            payload[name] = om.group(1)

    for tm in re.finditer(r'<textarea[^>]*name=["\']([^"\']+)["\'][^>]*>(.*?)</textarea>', html, re.I | re.S):
        payload[tm.group(1)] = tm.group(2).strip()

    return payload


def set_ocpp_endpoint_and_save(
    session: requests.Session,
    creds: ChargerCredentials,
    target_endpoint: str,
    timeout: int = 25,
) -> EndpointChangeResult:
    html_before = fetch_main_html(session, creds.ip, timeout=timeout)
    before = _extract_endpoint_from_html(html_before)

    payload = _extract_all_form_fields(html_before)
    # Campo crítico observado en UI
    payload["centralSystemAddress"] = target_endpoint
    # Trigger explícito de guardado observado en UI
    payload["ocpp_button"] = "Save"

    post_url = _base_url(creds.ip) + "/index_main.php"
    r = session.post(post_url, data=payload, timeout=timeout)
    r.raise_for_status()

    html_after = fetch_main_html(session, creds.ip, timeout=timeout)
    after = _extract_endpoint_from_html(html_after)

    saved = after == target_endpoint
    reason = "ok" if saved else "save_not_persisted"
    return EndpointChangeResult(before, target_endpoint, after, saved, reason)


def download_ocpp_logs_zip(session: requests.Session, ip: str, out_path: str, timeout: int = 180) -> Dict[str, Any]:
    url = _base_url(ip) + "/downloadOcppLogs.php"
    r = session.get(url, timeout=timeout, stream=True)
    r.raise_for_status()

    total = 0
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                total += len(chunk)

    return {
        "url": url,
        "saved_path": out_path,
        "bytes": total,
        "content_type": r.headers.get("content-type", ""),
        "content_disposition": r.headers.get("content-disposition", ""),
    }


def detect_free_mode_from_log_line(text: str) -> bool:
    return "#freecharging" in (text or "").lower()
