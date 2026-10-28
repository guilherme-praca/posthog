from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from posthog.dataclasses import frozen
from posthog.enums import LabeledStrEnum


class UnlayerError(Exception):
    pass


class UnlayerNotConfiguredError(UnlayerError):
    pass


class UnlayerRenderError(UnlayerError):
    pass


@dataclass(frozen=True)
class EmailTemplateSummary:
    id: UUID
    name: str
    subject: str


@dataclass(frozen=True)
class EmailTemplateContent:
    id: UUID
    name: str
    # The template's email body: subject, html, text and the editor design.
    email: dict[str, Any]


class TransactionalEmailError(Exception):
    """A send the caller has to fix before retrying. `code` is stable for API clients."""

    code = "invalid"


class TemplateNotSendable(TransactionalEmailError):
    code = "template_not_sendable"


class MarketingTemplate(TransactionalEmailError):
    code = "marketing_template"


class SenderUnavailable(TransactionalEmailError):
    code = "sender_unavailable"


class TemplateNotTransactional(TransactionalEmailError):
    code = "template_not_transactional"


class TransactionalEmailPaused(TransactionalEmailError):
    code = "transactional_email_paused"


class InvalidRecipient(TransactionalEmailError):
    code = "invalid_recipient"


class QuotaLimited(TransactionalEmailError):
    code = "quota_limited"


class InvalidIdempotencyKey(TransactionalEmailError):
    code = "invalid_idempotency_key"


class IdempotencyKeyInFlight(TransactionalEmailError):
    """The first request with this key is still being queued. Safe to retry shortly."""

    code = "idempotency_key_in_flight"


class IdempotencyKeyReused(TransactionalEmailError):
    code = "idempotency_key_reused"


class SendingSuspended(TransactionalEmailError):
    code = "sending_suspended"


class SendingPaused(TransactionalEmailError):
    code = "sending_paused"


class RecipientSuppressed(TransactionalEmailError):
    code = "recipient_suppressed"


class RecipientUnreachable(TransactionalEmailError):
    code = "recipient_unreachable"


class DeliveryUnavailable(Exception):
    """The email pipeline did not accept the send. Safe to retry."""


@frozen
class QueuedEmail:
    message_id: str
    # True when an earlier request with the same idempotency key already queued this email.
    replayed: bool = False


class EmailDeliveryStatus(LabeledStrEnum):
    QUEUED = "queued", "Queued"
    FAILED = "failed", "Failed"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    BOUNCED = "bounced", "Bounced"
    COMPLAINED = "complained", "Complained"


@frozen
class EmailStatus:
    message_id: str
    status: EmailDeliveryStatus
    created_at: datetime
    status_at: datetime
    # Why a send failed, or the bounce type of a bounced email.
    reason: str | None = None
