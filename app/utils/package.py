from dataclasses import dataclass

@dataclass
class Package: 
    id: str
    description: str
    latest_version: str
    dependencies: list[str]
   
