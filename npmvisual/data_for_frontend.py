from dataclasses import dataclass
from npmvisual._models.package import PackageData


@dataclass
class PackageDataAnalyzed:
    packageData: PackageData
    val: float
    in_degree: int | None = None
    out_degree: int | None = None

    @classmethod
    def from_package_data(cls, data: dict[str, PackageData]) -> dict[str, "PackageDataAnalyzed"]:
        results: dict[str, PackageDataAnalyzed] = {}
        for package_name, pd in data.items():
            results[package_name] = PackageDataAnalyzed(packageData=pd, val= -1)
        return results




