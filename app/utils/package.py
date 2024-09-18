from dataclasses import dataclass
from typing import Dict


@dataclass
class Package:
    id: str
    description: str
    latest_version: str
    dependencies: Dict[str, str]
