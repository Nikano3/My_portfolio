from fastapi import FastAPI, Depends, Header, HTTPException, status
from app.schemas.Auth import Registration, Login
from app.database import UserService, get_db, TokenChange
from app.utils.jwt_operations import Access, Refresh
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio
from app.utils.logger import logger
from database.users.models import main
app = FastAPI()
users = UserService()
tokench = TokenChange()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
#Создание базы данных с таблицами
asyncio.run(main())

@app.get("/")
async def index():
    logger.info("Requested registration page")
    return HTMLResponse(
        content=Path("frontend/templates/registration.html").read_text(encoding="utf-8"))


@app.get('/users')
async def get_users(db: AsyncSession = Depends(get_db),
                    check=Depends(Access.check)):
    logger.info("Request to get all users")
    if check["valid"] and not check["expired"]:
        users_data = await users.all_users(db)
        logger.info(f"Returning all users data. Count: {len(users_data)}")
        return users_data

    if check["expired"] and check["valid"]:
        logger.warning("Access token expired when getting all users")
        return JSONResponse(
            content={"error": "Token is expired, go to /refresh"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    logger.warning("Invalid access token when getting all users")
    return JSONResponse(
        content={"error": "Token is not valid"},
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.get('/users/{id}')
async def get_user(id: int, db: AsyncSession = Depends(get_db),
                   check=Depends(Access.check)):
    logger.info(f"Request to get user by id: {id}")
    if check["valid"] and not check["expired"]:
        user = await users.find_user(db, id)
        if user:
            logger.info(f"User found: id={id}")
        else:
            logger.warning(f"User not found: id={id}")
        return user

    if check["expired"] and check["valid"]:
        logger.warning(f"Access token expired when getting user id={id}")
        return JSONResponse(
            content={"error": "Token is expired, go to /refresh"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    logger.warning(f"Invalid access token when getting user id={id}")
    return JSONResponse(
        content={"error": "Token is not valid"},
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.post('/users/registration')
async def reg(registration: Registration, db: AsyncSession = Depends(get_db)):
    logger.info(f"Registration attempt: email={registration.email}")
    try:
        await users.register_user(db, registration.name, registration.email, registration.password)
        access_token = await Access.create(registration.email)
        refresh_token = await Refresh.create(db, registration.email)
        logger.info(f"User registered successfully: email={registration.email}")
        return JSONResponse(content={
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    except ValueError as e:
        logger.warning(f"Registration failed for email={registration.email}: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post('/users/login')
async def login(login: Login, db: AsyncSession = Depends(get_db)):
    logger.info(f"Login attempt: email={login.email}")
    try:
        if await users.login_check(db, login.email, login.password):
            logger.info(f"User logged in successfully: email={login.email}")
            return {"Login": "OK",
                    "Refresh_token": await Refresh.create(db, login.email),
                    "access_token": await Access.create(login.email)
                    }

        logger.warning(f"Failed login attempt: email={login.email}")
    except HTTPException as e:
        logger.error(f"Login error for email={login.email}: {e.detail}")
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})

    return JSONResponse(content={"Login": "Failed"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.post('/refresh')
async def access_refresh(token: str = Header(..., alias="token"), db: AsyncSession = Depends(get_db)):
    logger.info("Token refresh attempt")
    result = await Refresh.check(db, token)
    if result["expired"]:
        logger.warning("Refresh token expired")
        return JSONResponse(status_code=401, content={"error": "token is expired"})

    if not result["valid"]:
        logger.warning("Refresh token not valid")
        return JSONResponse(status_code=401, content={"error": "token is not valid"})

    new_access_token = await Access.create(result["email"])
    logger.info(f"Access token refreshed for email={result['email']}")
    return {"Ваш новый access токен": new_access_token}
