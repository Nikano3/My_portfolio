from passlib.context import CryptContext
from .logger import logger
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> bool | str:
    try:
        hashed_pass = pwd_context.hash(password)
        logger.info("Password hashed successfully")
        return hashed_pass
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        return False

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        verify = pwd_context.verify(plain_password, hashed_password)
        logger.info("Password verify successfully")
        return verify
    except Exception as e:
        logger.error(f"Error to verify password: {e}")
        return False