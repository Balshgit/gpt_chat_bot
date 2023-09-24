from os import urandom
from time import time

from flask import redirect, render_template, request, session, url_for
from flask_babel import refresh
from server.babel import get_languages, get_locale


class Website:
    def __init__(self, bp, url_prefix) -> None:
        self.bp = bp
        self.url_prefix = url_prefix
        self.routes = {
            "/": {
                "function": lambda: redirect(url_for("._index")),
                "methods": ["GET", "POST"],
            },
            "/chat/": {"function": self._index, "methods": ["GET", "POST"]},
            "/chat/<conversation_id>": {
                "function": self._chat,
                "methods": ["GET", "POST"],
            },
            "/change-language": {"function": self.change_language, "methods": ["POST"]},
            "/get-locale": {"function": self.get_locale, "methods": ["GET"]},
            "/get-languages": {"function": self.get_languages, "methods": ["GET"]},
        }

    def _chat(self, conversation_id):
        if "-" not in conversation_id:
            return redirect(url_for("._index"))

        return render_template("index.html", chat_id=conversation_id, url_prefix=self.url_prefix)

    def _index(self):
        return render_template(
            "index.html",
            chat_id=f"{urandom(4).hex()}-{urandom(2).hex()}-{urandom(2).hex()}-{urandom(2).hex()}-{hex(int(time() * 1000))[2:]}",
            url_prefix=self.url_prefix,
        )

    def change_language(self):
        data = request.get_json()
        session["language"] = data.get("language")
        refresh()
        return "", 204

    def get_locale(self):
        return get_locale()

    def get_languages(self):
        return get_languages()
