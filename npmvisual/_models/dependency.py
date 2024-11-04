from dataclasses import asdict, dataclass


@dataclass
class Dependency:
    package: str
    version: str

    def to_dict(self):
        return asdict(self)  # Convert Dependency to a dictionary
