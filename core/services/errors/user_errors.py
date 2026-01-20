# contains custom exceptions for the service layer


class InvalidCredentialsException(Exception):
    """
    Exception raised when invalid user credentials are provided
    """
    def __init__(self, message: str = "Invalid username or password"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(Exception):
    """
    Exception raised when a user is not found in the database
    """
    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsException(Exception):
    """
    Docstring raised when attempting to register a user that already exists
    """
    def __init__(self, message: str = "User with this email already exists"):
        self.message = message
        super().__init__(self.message)