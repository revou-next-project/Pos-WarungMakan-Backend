from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from config import dev
from routes import router as api_router
from databases.seed import seed_database
from scheduler.runner import start_scheduler
from fastapi.openapi.utils import get_openapi

# Lifespan for seeding the DB
async def lifespan(app: FastAPI):
    seed_database()
    start_scheduler() 
    yield

def create_app():
    config = dev.DevConfig()
    app = FastAPI(title=config.APP_NAME, lifespan=lifespan)

    # Add DBSessionMiddleware
    app.add_middleware(DBSessionMiddleware, db_url=config.DATABASE_URL)

    # Register your routers
    app.include_router(api_router)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 🔐 JWT Swagger UI config
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Pos Warung Makan API",
            version="0.1.0",
            description="An API for Pos Warung Makan Project",
            routes=app.routes,
        )

        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }

        for path in openapi_schema["paths"].values():
            for method in path.values():
                method.setdefault("security", [{"BearerAuth": []}])

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app

# Final app instance to run
app = create_app()
