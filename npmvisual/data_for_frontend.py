from dataclasses import dataclass
from npmvisual._models.package import PackageData


@dataclass
class DataForFrontend:
    packageData: PackageData
    val: float
    in_degree: int | None = None
    out_degree: int | None = None

    @classmethod
    def from_package_data(cls, data: dict[str, PackageData]) -> dict[str, "DataForFrontend"]:
        results: dict[str, DataForFrontend] = {}
        for package_name, pd in data.items():
            results[package_name] = DataForFrontend(packageData=pd, val= -1)
        return results




