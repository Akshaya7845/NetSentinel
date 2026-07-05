from pydantic import BaseModel
from datetime import datetime
from typing import Dict


class NetworkStatus(BaseModel):
    network: str
    api: str
    containers_running: int
    containers: Dict[str, str]
    timestamp: datetime