import os
from typing import final

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
_ = load_dotenv(os.path.join(basedir, ".env"))


@final
class Config:
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
    NEO4J_HOST = os.environ.get("NEO4J_HOST")
    NEO4J_DB = os.environ.get("NEO4J_DB")
    NEO4J_PORT = os.environ.get("NEO4J_PORT")
