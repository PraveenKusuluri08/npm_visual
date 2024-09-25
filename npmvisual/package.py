from dataclasses import dataclass
from typing import Dict


@dataclass
class Package:
    id: str
    description: str
    latest_version: str
    dependencies: Dict[str, str]

    # def __init__(self, fname):
    # dict.__init__(self, fname=fname)
