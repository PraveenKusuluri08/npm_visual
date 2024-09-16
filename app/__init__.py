from flask import Flask,jsonify
import os
from app.utils import utils
import networkx as nx

def create_app():
    app=Flask(__name__)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


    @app.route("/npm")
    def npm():
        return jsonify(utils.utils.get_data())

    @app.route('/dependencies/<package_name>', methods=['GET'])
    # print('api route called')
    def get_package_dependencies(package_name):
        graph = utils.build_graph(package_name)

        graph_data = nx.node_link_data(graph)
        return jsonify(graph_data)

    # Configure our app here. if we want to use blueprints later, we can do that. 
    return app

