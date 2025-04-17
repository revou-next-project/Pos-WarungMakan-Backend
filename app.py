from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db
from config import dev
from fastapi.middleware.cors import CORSMiddleware
from routes import app as api_app
from databases.seed import seed_database

# Define the lifespan function without the unused app argument
async def lifespan(app: FastAPI):
    # Seed the database when the app starts
    seed_database()
    yield  # Yield at the end of the lifespan function to signal completion

def create_app():
    config = dev.DevConfig()
    app = FastAPI(title=config.APP_NAME, lifespan=lifespan)  # Pass lifespan function directly

    # Add DBSessionMiddleware for managing database sessions
    app.add_middleware(DBSessionMiddleware, db_url=config.DATABASE_URL)

    # Include your routers
    app.include_router(api_app.router)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

# Create the FastAPI app
app = create_app()
