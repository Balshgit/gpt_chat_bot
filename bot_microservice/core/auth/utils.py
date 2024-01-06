import hashlib

from settings.config import settings


def create_password_hash(password: str) -> str:
    if not settings.SALT:
        return password
    return hashlib.sha256((password + settings.SALT.get_secret_value()).encode()).hexdigest()
