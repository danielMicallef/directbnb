from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field
from typing import Optional


class StripeSession(BaseModel):
    client_reference_id: UUID = Field(None, alias="client_reference_id")


class StripeEventData(BaseModel):
    object: StripeSession

class StripeEventType(StrEnum):
    CHECKOUT_COMPLETED = "checkout.session.completed"
    CHECKOUT_EXPIRED = "checkout.session.expired"


class StripeEvent(BaseModel):
    type: StripeEventType | str
    data: StripeEventData

    def get_lead_registration_id(self) -> str:
        return self.data.object.client_reference_id
