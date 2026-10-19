"""Fail closed: actions, never arbitrary command strings."""


class ToolPolicy:
    ACTIONS = {"flush_dns": ("ipconfig", "/flushdns")}

    @classmethod
    def check(cls, action):
        return isinstance(action, str) and action in cls.ACTIONS
