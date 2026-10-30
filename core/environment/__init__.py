from .environment import _Settings

Config: _Settings | None = None

def init_settings():
    global Config
    Config = _Settings()

