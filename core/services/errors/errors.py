# contains custom exceptions for the service layer


class InvalidCredentialsException(Exception):
    """
    Exception raised for invalid user credentials.
    """
    def __init__(self, message: str = "Invalid username or password"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(Exception):
    """
    Exception raised when a user is not found in the database.
    """
    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(self.message)