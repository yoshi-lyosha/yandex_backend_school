from app.core import config


def get_server_api():
    if config.server_port:
        server_name = f"http://{config.server_host}:{config.server_port}"
    else:
        server_name = f"http://{config.server_host}"
    return server_name


class IntValue:
    def __eq__(self, other):
        try:
            int(other)
        except (ValueError, TypeError):
            return False
        return True
