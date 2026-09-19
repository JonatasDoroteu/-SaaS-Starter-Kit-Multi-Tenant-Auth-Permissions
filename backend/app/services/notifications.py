from __future__ import annotations

import httpx

from app.core.config import get_settings


class NotificationDeliveryError(Exception):
    """Levantado quando o notification-service não aceita a notificação.
    Nunca deve derrubar o fluxo principal que a disparou — notificar é
    efeito colateral, não o motivo da requisição do usuário."""


async def send_notification(
    *,
    organization_id: int,
    user_id: str,
    type: str,
    title: str,
    body: str,
) -> None:
    settings = get_settings()
    payload = {
        "organizationId": str(organization_id),
        "userId": user_id,
        "type": type,
        "title": title,
        "body": body,
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(
                f"{settings.notification_service_url}/notifications",
                json=payload,
                headers={"X-Service-Key": settings.notification_service_key},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise NotificationDeliveryError(str(exc)) from exc