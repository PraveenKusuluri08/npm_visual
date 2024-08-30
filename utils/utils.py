import requests
import networkx as nx
import matplotlib.pyplot as plt

def get_data():
    package_names = ["express","dotenv","loadash","axios"]

    data = []

    for package_name in package_names:
        url = f"https://registry.npmjs.org/{package_name}"
        response = requests.get(url)
        if response.status_code == 200:
            r_dict = response.json()
            
            latest_version = r_dict.get("dist-tags", {}).get("latest")
            
            dependencies = r_dict.get("versions", {}).get(latest_version, {}).get("dependencies", None)
            
            package_info = {
                "_id": r_dict.get("_id"),
                "description": r_dict.get("description"),
                "latest_version": latest_version,
                "dependencies": dependencies
            }
            data.append(package_info)
        else:
            print(f"Failed to fetch data for {package_name}, status code: {response.status_code}")

    return data