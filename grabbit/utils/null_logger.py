from logging import Logger

class NullLogger(Logger):
    """ A logger that logs nothing """

    def __init__(self):
        super().__init__("NullLogger")

    def _log(self, *args, **kwargs):
        pass
