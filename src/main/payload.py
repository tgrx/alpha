from typing import Dict
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class RequestT(BaseModel):
    body: str = Field(...)
    more_body: bool = Field(default=False)
    type: str = Field(...)  # noqa: A003,VNE003


class ScopeAsgiT(BaseModel):
    spec_version: Optional[str] = Field(default=None)
    version: str = Field(...)


class HostPortT(BaseModel):
    host: str = Field(...)
    port: Optional[int] = Field(default=None)


class ScopeT(BaseModel):
    asgi: ScopeAsgiT = Field(...)
    client: HostPortT = Field(...)
    headers: Dict[str, str] = Field(default_factory=dict)
    http_version: str = Field(...)
    method: str = Field(...)
    path: str = Field(...)
    query_string: str = Field(...)
    raw_path: str = Field(...)
    root_path: str = Field(...)
    scheme: str = Field(...)
    server: HostPortT = Field(...)
    type: str = Field(...)  # noqa: A003,VNE003


class PayloadT(BaseModel):
    request: RequestT = Field(...)
    scope: ScopeT = Field(...)
