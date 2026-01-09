class BaseException(Exception):
    """ An  error occurred """
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message or self.__class__.__doc__


class CommandError(BaseException):
    """ Invalid usage of CLI. """
