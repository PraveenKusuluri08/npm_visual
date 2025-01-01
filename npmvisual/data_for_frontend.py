from dataclasses import dataclass
from typing import Any
from npmvisual._models.package import PackageData

@dataclass
class PackageDataAnalyzed:
    id: str
    packageData: PackageData | None
    val: float | None
    in_degree: int | None = None
    out_degree: int | None = None
    color: str | None = None
    color_id: int | None = None

    @classmethod
    def from_package_data(cls, data: dict[str, PackageData]) -> dict[str, "PackageDataAnalyzed"]:
        results: dict[str, PackageDataAnalyzed] = {}
        for package_name, pd in data.items():
            results[package_name] = PackageDataAnalyzed(id = package_name, packageData=pd, val= -1)
        return results

    def to_dict(self) -> dict[str, Any]:
        # Convert the PackageDataAnalyzed object to a dictionary
        return {
            "id": self.id,
            "packageData": None,
            "val": self.val,
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "color": self.color,
            "color_id": self.color_id
        }

@dataclass
class Edge:
    index: int
    source: Any
    target: Any


@dataclass
class DataForFrontend:
    links: list[Any]
    nodes: list[PackageDataAnalyzed]
    graph: dict
    multigraph: bool
    directed: bool


