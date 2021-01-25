from pydantic import BaseModel
from typing import Any, List, Dict


class Submission(BaseModel):
    participant_id: str
    entries: List[Dict[str, Any]]
