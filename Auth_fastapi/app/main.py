from fastapi import FastAPI, Depends, Header, HTTPException, status
from app.schemas.schema import Registration, Login
from app.database import UserService, get_db, TokenChange
from app.utils.jwt_operations import Access, Refresh
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import app.utils.logger
app = FastAPI()
users = UserService()
tokench = TokenChange()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")


@app.get("/")
async def index():
    return HTMLResponse(
        content=Path("frontend/templates/registration.html").read_text(encoding="utf-8"))


@app.get('/users')
async def get_users(db: AsyncSession = Depends(get_db),
                    check=Depends(Access.check)):
    if check["valid"] and not check["expired"]:
        users_data = await users.all_users(db)
        return users_data

    if check["expired"] and check["valid"]:
        return JSONResponse(
            content={"error": "Token is expired, go to /refresh"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return JSONResponse(
        content={"error": "Token is not valid"},
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.get('/users/{id}')
async def get_user(id: int, db: AsyncSession = Depends(get_db),
                   check=Depends(Access.check)):
    if check["valid"] and not check["expired"]:
        return await users.find_user(db, id)

    if check["expired"] and check["valid"]:
        return JSONResponse(
            content={"error": "Token is expired, go to /refresh"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    return JSONResponse(
        content={"error": "Token is not valid"},
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.post('/users/registration')
async def reg(registration: Registration, db: AsyncSession = Depends(get_db)):
    try:
        await users.register_user(db, registration.name, registration.email, registration.password)
        access_token = await Access.create(registration.email)
        refresh_token = await Refresh.create(db, registration.email)
        return JSONResponse(content={
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post('/users/login')
async def login(login: Login, db: AsyncSession = Depends(get_db)):
    try:
        if await users.login_check(db, login.email, login.password):
            return {"Login": "OK",
                    "Refresh_token": await Refresh.create(db, login.email),
                    "access_token": await Access.create(login.email)
                    }

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})

    return JSONResponse(content={"Login": "Failed"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.post('/refresh')
async def access_refresh(token: str = Header(..., alias="token"), db: AsyncSession = Depends(get_db)):
    result = await Refresh.check(db, token)
    if result["expired"]:
        return JSONResponse(status_code=401, content={"error": "token is expired"})

    if not result["valid"]:
        return JSONResponse(status_code=401, content={"error": "token is not valid"})
    return {"Ваш новый access токен": await Access.create(result["email"])}
