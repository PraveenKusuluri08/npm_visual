from typing import Dict

from flask import json

from npmvisual.package import Package


def save(data: Dict[str, Package]):
    with open("data.json", "w") as f:
        json_string = json.dumps([ob.__dict__ for ob in data])
        json.dump(data, f, ensure_ascii=False)


def load() -> Dict[str, Package]:
    with open("data.json") as data_file:
        data_loaded = json.load(data_file)
        data = {}
        for key, p in data_loaded:
            next = Package(**p)
            data[key] = next
        return data
