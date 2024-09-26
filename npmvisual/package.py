from dataclasses import dataclass
from typing import Dict


@dataclass
class Package:
    id: str
    description: str
    latest_version: str
    dependencies: Dict[str, str]

    def __init__(self, r_dict):
        self.id = r_dict.get("_id")
        self.description = r_dict.get("description")
        self.latest_version = r_dict.get("dist-tags", {}).get("latest")

        # some packages have no dependencies. represent this as an empty dict
        self.dependencies: Dict[str, str] = (
            r_dict.get("versions", {})
            .get(self.latest_version, {})
            .get("dependencies", {})
        )

    # def __init__(self, fname):
    # dict.__init__(self, fname=fname)
