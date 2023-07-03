""" Field Not Set Exception """

class InvalidId(Exception):
    """ Field Not Set Exception """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message