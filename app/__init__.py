from flask import Flask


def create_app():
    app=Flask(__name__)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Configure our app here. if we want to use blueprints later, we can do that. 
    return app
