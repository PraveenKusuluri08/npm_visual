import requests
import networkx as nx
import matplotlib.pyplot as plt

def create_graph():
    G = nx.Graph()

    data = get_data()

    for package in data:
        main_package = package["_id"]

        G.add_node(main_package, label=main_package)
        for dependency, _ in package["dependencies"].items():
            G.add_node(dependency, label=dependency)
            G.add_edge(dependency, main_package)

    pos = nx.spring_layout(G)  
    nx.draw(G, pos, with_labels=False, node_size=500, node_color="lightblue") 

    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=10)

    nx.draw_networkx_nodes(G, pos, nodelist=[main_package], node_color='red', node_size=700)

    plt.savefig("graph.png")
    
    
def get_data():
    package_names = ["express"]

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


create_graph()