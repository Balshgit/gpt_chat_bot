import secrets
from functools import lru_cache
from json import load
from typing import Any

from flask import Flask
from server.babel import create_babel
from server.backend import Backend_Api
from server.bp import bp
from server.website import Website


@lru_cache(maxsize=None)
def get_config() -> dict[str, Any]:
    # Load configuration from config.json
    with open("config.json", "r") as config_file:
        return load(config_file)


def create_app() -> Flask:
    config = get_config()

    url_prefix = config["url_prefix"]
    # Create the app
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)

    # Set up Babel
    create_babel(app)

    # Set up the website routes
    site = Website(bp, url_prefix)
    for route in site.routes:
        bp.add_url_rule(
            route,
            view_func=site.routes[route]["function"],
            methods=site.routes[route]["methods"],
        )

    # Set up the backend API routes
    backend_api = Backend_Api(bp, config)
    for route in backend_api.routes:
        bp.add_url_rule(
            route,
            view_func=backend_api.routes[route]["function"],
            methods=backend_api.routes[route]["methods"],
        )

    # Register the blueprint
    app.register_blueprint(bp, url_prefix=url_prefix)

    return app


if __name__ == "__main__":
    config = get_config()
    site_config = config["site_config"]
    url_prefix = config["url_prefix"]
    app = create_app()
    # Run the Flask server
    print(f"Running on {site_config['port']}{url_prefix}")
    app.run(**site_config)
    print(f"Closing port {site_config['port']}")
