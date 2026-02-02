import json
import logging
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)


def normalize_phone(value: str | None) -> str:
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return ""
    digits = digits.lstrip("0")
    if not digits.startswith("55") and len(digits) in (10, 11):
        digits = f"55{digits}"
    return digits


def _should_log() -> bool:
    return getattr(settings, "WHATSAPP_ZAPI_LOG_REQUESTS", True)


def _mask_token(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep * 2:
        return "*" * len(value)
    return f"{value[:keep]}...{value[-keep:]}"


def _mask_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return ""
    if len(digits) <= 4:
        return "*" * len(digits)
    return f"{'*' * (len(digits) - 4)}{digits[-4:]}"


def _sanitize_message(value: str, limit: int = 160) -> str:
    if not value:
        return ""
    compact = re.sub(r"\s+", " ", value).strip()
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit]}..."


def _mask_endpoint(endpoint: str, instance_id: str, token: str) -> str:
    masked = endpoint
    if instance_id:
        masked = masked.replace(f"/instances/{instance_id}/", "/instances/****/")
    if token:
        masked = masked.replace(f"/token/{token}/", f"/token/{_mask_token(token)}/")
    return masked


def _log_request(endpoint: str, instance_id: str, token: str, headers: dict, phone: str, message: str) -> None:
    if not _should_log():
        return
    masked_headers = {}
    for key, value in headers.items():
        if key.lower() in {"client-token", "authorization"}:
            masked_headers[key] = _mask_token(str(value))
        else:
            masked_headers[key] = value
    payload_info = {
        "phone": _mask_phone(phone),
        "message_preview": _sanitize_message(message),
        "message_length": len(message or ""),
    }
    logger.info(
        "WhatsApp request POST %s headers=%s payload=%s",
        _mask_endpoint(endpoint, instance_id, token),
        masked_headers,
        payload_info,
    )


def _log_response(status: int, body: str) -> None:
    if not _should_log():
        return
    logger.info(
        "WhatsApp response status=%s body=%s body_length=%s",
        status,
        _sanitize_message(body, limit=240),
        len(body or ""),
    )


def _resolve_config() -> dict[str, str]:
    instance_id = getattr(settings, "WHATSAPP_ZAPI_INSTANCE_ID", "")
    token = getattr(settings, "WHATSAPP_ZAPI_TOKEN", "")
    base_url = getattr(settings, "WHATSAPP_ZAPI_BASE_URL", "https://api.z-api.io")
    client_token = getattr(settings, "WHATSAPP_ZAPI_CLIENT_TOKEN", "")
    try:
        from .models import WhatsappSettings

        stored = WhatsappSettings.objects.first()
    except (OperationalError, ProgrammingError):
        stored = None

    if stored:
        stored_base = (stored.zapi_base_url or "").strip()
        stored_instance = (stored.zapi_instance_id or "").strip()
        stored_token = (stored.zapi_token or "").strip()
        stored_client_token = (stored.zapi_client_token or "").strip()
        if stored_base:
            base_url = stored_base
        if stored_instance:
            instance_id = stored_instance
        if stored_token:
            token = stored_token
        if stored_client_token:
            client_token = stored_client_token
    return {
        "base_url": base_url,
        "instance_id": instance_id,
        "token": token,
        "client_token": client_token,
    }


def send_text(phone: str, message: str) -> dict[str, str | bool]:
    config = _resolve_config()
    instance_id = config["instance_id"]
    token = config["token"]
    base_url = config["base_url"]
    client_token = config["client_token"]
    if not instance_id or not token:
        logger.warning("WhatsApp envio ignorado: credenciais nao configuradas.")
        return {"ok": False, "error": "missing_credentials"}
    base_url = base_url.rstrip("/")
    endpoint = f"{base_url}/instances/{instance_id}/token/{token}/send-text"

    normalized = normalize_phone(phone)
    if not normalized:
        return {"ok": False, "error": "invalid_phone"}
    if not message:
        return {"ok": False, "error": "empty_message"}

    payload = json.dumps({"phone": normalized, "message": message}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if client_token:
        headers["client-token"] = client_token
    _log_request(endpoint, instance_id, token, headers, normalized, message)
    request = Request(
        endpoint,
        data=payload,
        headers=headers,
        method="POST",
    )
    timeout = getattr(settings, "WHATSAPP_ZAPI_TIMEOUT", 15)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            status = response.getcode()
        _log_response(status or 200, body)
        return {"ok": True, "response": body}
    except HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        _log_response(exc.code, body)
        logger.warning("WhatsApp erro HTTP %s: %s", exc.code, exc)
        return {"ok": False, "error": f"http_{exc.code}"}
    except URLError as exc:
        logger.warning("WhatsApp erro de conexao: %s", exc)
        return {"ok": False, "error": "connection_error"}
