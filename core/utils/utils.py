import bcrypt


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt algorithm.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())