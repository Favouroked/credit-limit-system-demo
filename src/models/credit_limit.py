from datetime import datetime

from pydantic import BaseModel


class CreditLimitParams(BaseModel):
    user_id: str
    start: datetime
    end: datetime


class DeployCreditLimitPayload(BaseModel):
    user_id: str
    credit_limit_id: str
