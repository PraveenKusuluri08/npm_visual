# import logging
# from logging import config as logging_config

from npmvisual import create_app

# import flask
# app = flask.Flask(__name__)
app = create_app()


# if __name__ == "__main__":
#     log_server = logging_config.listen()
#     log_server.start()
#     # Set the level to INFO by default.
#     app.logger.setLevel(logging.INFO)
#     try:
#         app.run()
#     finally:
#         logging_config.stopListening()
#         log_server.join()
