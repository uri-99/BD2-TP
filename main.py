from fastapi import FastAPI
from fastapi.security import OAuth2PasswordRequestForm

from core.auth.models import *
from core.auth.utils import *
from v1.endpoints import users, documents, folders
from core.settings import Settings

settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version="0.0.1"
)

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(folders.router)

app.openapi_tags = [
    users.tag_metadata,
    documents.tag_metadata,
    folders.tag_metadata
]


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user['_id']), "username": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=LoggedUser)
async def read_users_me(current_user: LoggedUser = Depends(get_current_user)):
    return current_user
