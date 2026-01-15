from passlib.context import CryptContext


pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt algorithm.
    """
    return pwd_hasher.hash(password)


def verify_password(unhashed_passwrd: str, hashed_password:str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    """
    return pwd_hasher.verify(unhashed_passwrd, hashed_password)