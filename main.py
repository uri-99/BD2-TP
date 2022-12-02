from fastapi import FastAPI
from v1.endpoints import users, documents, folders, favorites
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
app.include_router(favorites.router)

app.openapi_tags = [
    users.tag_metadata,
    documents.tag_metadata,
    folders.tag_metadata,
    favorites.tag_metadata
]

# load_dotenv(settings.Config.env_file)

# DB Connection code example
# client = MongoClient(os.environ.get(settings.mongo_pass))
# BD2 = client.BD2
# notes = BD2.File
# users = BD2.User
# print(notes.find_one())
# print(users.find_one())
# client.close()
