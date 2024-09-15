from flask import Flask,jsonify
import os
from utils import utils
import networkx as nx

def create_app():
    app=Flask(__name__)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Configure our app here. if we want to use blueprints later, we can do that. 
    return app

"""
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/npm")
def npm():
    return jsonify(utils.utils.get_data())

@app.route('/api/dependencies/<package_name>', methods=['GET'])
def get_package_dependencies(package_name):
    graph = utils.build_graph(package_name)

    graph_data = nx.node_link_data(graph)
    return jsonify(graph_data)

PORT = os.getenv("HTTP_PORT") or 8080

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

"""
