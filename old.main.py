from flask import Flask,jsonify
import os
from utils import utils
import utils.utils 
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/npm")
def npm():
    return jsonify(utils.utils.get_data())
PORT = os.getenv("HTTP_PORT") or 8080

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)