from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional
from uuid import uuid4

import pytz
from pydantic import BaseModel, model_validator

timezone = pytz.timezone("UTC")


class BaseEntity(ABC, BaseModel):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    @classmethod
    @abstractmethod
    def get_table_columns(cls) -> List[str]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_table_name(cls) -> str:
        raise NotImplementedError()

    @model_validator(mode="before")
    @classmethod
    def populate_default_fields(cls, data: Any) -> Any:
        if "id" not in data:
            data["id"] = str(uuid4())
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone)
        data["updated_at"] = datetime.now(timezone)
        return data

    class Config:
        use_enum_values = True
