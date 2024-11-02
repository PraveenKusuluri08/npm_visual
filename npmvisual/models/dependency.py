from dataclasses import dataclass


@dataclass
class Dependency:
    package: str
    version: str
