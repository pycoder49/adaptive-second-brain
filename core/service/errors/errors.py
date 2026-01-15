# contains custom exceptions for the service layer


class InvalidCredentialsException(Exception):
    """
    Exception raised for invalid user credentials.
    """
    def __init__(self, message: str = "Invalid username or password"):
        self.message = message
        super().__init__(self.message)