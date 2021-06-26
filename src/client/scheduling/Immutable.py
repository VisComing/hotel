from pydantic import BaseModel as PydanticBaseModel


class Immutable(PydanticBaseModel):
    class Config:
        frozen = True
