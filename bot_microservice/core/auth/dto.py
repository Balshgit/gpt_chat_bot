from dataclasses import dataclass


@dataclass
class UserIsBannedDTO:
    is_banned: bool = False
    ban_reason: str | None = None
