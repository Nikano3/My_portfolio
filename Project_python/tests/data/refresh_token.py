from datetime import datetime, timezone, timedelta
from pydantic import EmailStr
import uuid
import jwt
from app.config import settings
from app.database import TokenChange
from sqlalchemy.ext.asyncio import AsyncSession
async def create_expired_refresh(db: AsyncSession, email: EmailStr,
                                 expires_delta: timedelta = timedelta(hours=24)):
    time = datetime.now(timezone.utc)
    exp = time - expires_delta
    jti = uuid.uuid4()
    iat = time
    data = {
        "email": email,
        "exp": exp,  # Expiration Time (время истечения)
        "iat": time,  # Issued At (время выпуска)
        "jti": str(jti)  # JWT ID
    }
    await TokenChange.token_create(db, user_email=email, jti=jti, iat=iat, exp=exp)
    return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")
