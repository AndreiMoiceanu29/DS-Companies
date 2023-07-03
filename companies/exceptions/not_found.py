""" Field Not Set Exception """

class NotFound(Exception):
    """ Field Not Set Exception """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message